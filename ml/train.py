"""
Train a skin concern classifier on the concerns dataset.

Classes (5): acne_pimples, blackheads_whiteheads, dandruff, dark_circles,
             hyperpigmentation_dark_spots

Architecture: EfficientNetB0 (ImageNet pretrained) + custom head
Strategy:
  Phase 1 — freeze base, train head only   (fast convergence)
  Phase 2 — unfreeze top 30 layers, fine-tune (accuracy boost)

Input: raw [0, 255] pixels — Rescaling(1/255) is baked into the model.
"""
import os
import pathlib

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, regularizers
from tensorflow.keras.applications import EfficientNetB0

# ── Config ────────────────────────────────────────────────────────────────────
DATA_DIR          = os.environ.get("DATA_DIR", "backend/dataset/concerns")
MODEL_OUTPUT_PATH = os.environ.get("MODEL_OUTPUT_PATH", "models/skin_concern_model.keras")
IMG_SIZE          = (224, 224)
BATCH_SIZE        = int(os.environ.get("BATCH_SIZE", "32"))
PHASE1_EPOCHS     = int(os.environ.get("PHASE1_EPOCHS", "20"))
PHASE2_EPOCHS     = int(os.environ.get("PHASE2_EPOCHS", "30"))
VALIDATION_SPLIT  = float(os.environ.get("VALIDATION_SPLIT", "0.2"))
SEED              = 42

LABELS = sorted([
    d.name for d in pathlib.Path(DATA_DIR).iterdir()
    if d.is_dir() and not d.name.startswith("_")
])
NUM_CLASSES = len(LABELS)

print(f"Classes ({NUM_CLASSES}): {LABELS}")
print(f"Output model: {MODEL_OUTPUT_PATH}")


# ── Dataset ───────────────────────────────────────────────────────────────────
def make_datasets():
    train_ds = tf.keras.utils.image_dataset_from_directory(
        DATA_DIR,
        validation_split=VALIDATION_SPLIT,
        subset="training",
        seed=SEED,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="categorical",
        class_names=LABELS,
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        DATA_DIR,
        validation_split=VALIDATION_SPLIT,
        subset="validation",
        seed=SEED,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="categorical",
        class_names=LABELS,
    )
    return train_ds, val_ds


# Augmentation applied only during training, after caching raw pixels
_augment = tf.keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.15),
    layers.RandomZoom(0.15),
    layers.RandomBrightness(0.15),
    layers.RandomContrast(0.15),
], name="augmentation")


def prepare(ds, augment=False):
    # Cache raw [0,255] pixels first, then augment so each epoch sees different transforms
    ds = ds.cache()
    if augment:
        ds = ds.map(
            lambda x, y: (_augment(tf.cast(x, tf.float32), training=True), y),
            num_parallel_calls=tf.data.AUTOTUNE,
        )
    else:
        ds = ds.map(
            lambda x, y: (tf.cast(x, tf.float32), y),
            num_parallel_calls=tf.data.AUTOTUNE,
        )
    return ds.prefetch(tf.data.AUTOTUNE)


def compute_class_weights(train_ds_raw):
    counts = np.zeros(NUM_CLASSES)
    for _, labels_batch in train_ds_raw.unbatch():
        counts[np.argmax(labels_batch.numpy())] += 1
    total = counts.sum()
    weights = {i: total / (NUM_CLASSES * c) for i, c in enumerate(counts)}
    print("Class weights:", {LABELS[i]: round(w, 3) for i, w in weights.items()})
    return weights


# ── Model ─────────────────────────────────────────────────────────────────────
def build_model(num_classes: int):
    """
    EfficientNetB0 has its own internal preprocessing — pass raw [0, 255] pixels directly.
    Do NOT add a Rescaling layer; it breaks the ImageNet pretrained weights.
    """
    base = EfficientNetB0(
        include_top=False,
        weights="imagenet",
        input_shape=(*IMG_SIZE, 3),
    )
    base.trainable = False

    inputs = tf.keras.Input(shape=(*IMG_SIZE, 3), name="image_input")
    x = base(inputs, training=False)   # training=False keeps BN in inference mode when frozen
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.4)(x)
    x = layers.Dense(256, activation="relu",
                     kernel_regularizer=regularizers.l2(1e-4))(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    return tf.keras.Model(inputs, outputs)


def get_callbacks(model_path: str):
    return [
        tf.keras.callbacks.ModelCheckpoint(
            model_path,
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1,
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy",
            patience=7,
            restore_best_weights=True,
            verbose=1,
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.3,
            patience=4,
            min_lr=1e-7,
            verbose=1,
        ),
    ]


# ── Training ──────────────────────────────────────────────────────────────────
def main():
    os.makedirs(os.path.dirname(MODEL_OUTPUT_PATH) or ".", exist_ok=True)

    train_ds_raw, val_ds_raw = make_datasets()
    train_ds = prepare(train_ds_raw, augment=True)
    val_ds   = prepare(val_ds_raw,   augment=False)

    class_weights = compute_class_weights(train_ds_raw)

    # ── Phase 1: frozen base, train head only ─────────────────────────────────
    print("\n=== Phase 1: Training head (base frozen) ===")
    model = build_model(NUM_CLASSES)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(1e-3),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    model.summary()

    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=PHASE1_EPOCHS,
        class_weight=class_weights,
        callbacks=get_callbacks(MODEL_OUTPUT_PATH),
    )

    # ── Phase 2: unfreeze top 30 layers of EfficientNetB0 ────────────────────
    print("\n=== Phase 2: Fine-tuning top layers ===")
    model = tf.keras.models.load_model(MODEL_OUTPUT_PATH)

    # Find the EfficientNetB0 sub-model (it's a tf.keras.Model, not a plain layer)
    efficientnet = next(l for l in model.layers if isinstance(l, tf.keras.Model))
    efficientnet.trainable = True
    # Freeze all but the last 30 layers
    for layer in efficientnet.layers[:-30]:
        layer.trainable = False

    model.compile(
        optimizer=tf.keras.optimizers.Adam(1e-5),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=PHASE2_EPOCHS,
        class_weight=class_weights,
        callbacks=get_callbacks(MODEL_OUTPUT_PATH),
    )

    # ── Final evaluation ──────────────────────────────────────────────────────
    print("\n=== Final Evaluation ===")
    model = tf.keras.models.load_model(MODEL_OUTPUT_PATH)
    loss, acc = model.evaluate(val_ds, verbose=1)
    print(f"\nVal accuracy: {acc:.4f}  |  Val loss: {loss:.4f}")
    print(f"Model saved to: {MODEL_OUTPUT_PATH}")
    print(f"Class order:    {LABELS}")


if __name__ == "__main__":
    main()
