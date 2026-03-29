"""Run this once to write ml/train.py — works in fish, bash, zsh."""
import os

content = """\
import os, sys
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing.image import ImageDataGenerator

DATA_DIR          = os.environ.get("DATA_DIR", "dataset")
MODEL_OUTPUT_PATH = os.environ.get("MODEL_OUTPUT_PATH", "models/model.keras")
IMG_SIZE          = (224, 224)
BATCH_SIZE        = int(os.environ.get("BATCH_SIZE", "32"))
PHASE1_EPOCHS     = int(os.environ.get("PHASE1_EPOCHS", "15"))
PHASE2_EPOCHS     = int(os.environ.get("PHASE2_EPOCHS", "15"))
LABELS            = ["combination", "dry", "normal", "oily"]
NUM_CLASSES       = 4
TRAIN_DIR         = os.path.join(DATA_DIR, "train")
VALID_DIR         = os.path.join(DATA_DIR, "valid")


def build_model():
    base = MobileNetV2(input_shape=(*IMG_SIZE, 3), include_top=False, weights="imagenet")
    base.trainable = False
    inp = tf.keras.Input(shape=(*IMG_SIZE, 3))
    x = base(inp, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(256, activation="relu")(x)
    x = layers.Dropout(0.4)(x)
    out = layers.Dense(NUM_CLASSES, activation="softmax")(x)
    return models.Model(inp, out), base


def get_generators():
    tr = ImageDataGenerator(
        rescale=1.0/255, horizontal_flip=True,
        rotation_range=15, zoom_range=0.10,
        brightness_range=[0.8, 1.2],
        width_shift_range=0.05, height_shift_range=0.05,
        fill_mode="nearest",
    )
    va = ImageDataGenerator(rescale=1.0/255)
    kw = dict(target_size=IMG_SIZE, batch_size=BATCH_SIZE,
              class_mode="categorical", classes=LABELS)
    tg = tr.flow_from_directory(TRAIN_DIR, shuffle=True, **kw)
    vg = va.flow_from_directory(VALID_DIR, shuffle=False, **kw)
    return tg, vg


def get_class_weights(gen):
    counts = np.bincount(gen.classes)
    total  = counts.sum()
    w = {i: total / (NUM_CLASSES * c) for i, c in enumerate(counts)}
    print("Class weights:", {LABELS[i]: round(v, 3) for i, v in w.items()})
    return w


def train():
    print(f"TF {tf.__version__} | dataset={DATA_DIR} | output={MODEL_OUTPUT_PATH}")
    if not os.path.isdir(TRAIN_DIR):
        print("ERROR: TRAIN_DIR not found:", TRAIN_DIR)
        sys.exit(1)

    model, base = build_model()
    tg, vg = get_generators()
    print(f"Train={tg.samples}  Valid={vg.samples}")
    if tg.samples == 0:
        print("ERROR: no images found. Check DATA_DIR and folder names.")
        sys.exit(1)

    cw = get_class_weights(tg)
    os.makedirs(os.path.dirname(MODEL_OUTPUT_PATH) or ".", exist_ok=True)

    print(f"\\n=== Phase 1: head only ({PHASE1_EPOCHS} epochs) ===")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(1e-3),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    model.fit(tg, validation_data=vg, epochs=PHASE1_EPOCHS, class_weight=cw,
              callbacks=[
                  tf.keras.callbacks.EarlyStopping(patience=4, restore_best_weights=True, monitor="val_accuracy"),
                  tf.keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=2),
              ])

    print(f"\\n=== Phase 2: fine-tune top 30 layers ({PHASE2_EPOCHS} epochs) ===")
    base.trainable = True
    for layer in base.layers[:-30]:
        layer.trainable = False
    model.compile(
        optimizer=tf.keras.optimizers.Adam(1e-5),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    model.fit(tg, validation_data=vg, epochs=PHASE2_EPOCHS, class_weight=cw,
              callbacks=[
                  tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True, monitor="val_accuracy"),
                  tf.keras.callbacks.ModelCheckpoint(
                      MODEL_OUTPUT_PATH, save_best_only=True, monitor="val_accuracy", verbose=1),
              ])

    model.save(MODEL_OUTPUT_PATH)
    loss, acc = model.evaluate(vg, verbose=0)
    print(f"\\nSaved -> {MODEL_OUTPUT_PATH}  |  val_acc={acc:.4f}  loss={loss:.4f}")

    label_map = MODEL_OUTPUT_PATH.replace(".keras", "_labels.txt")
    with open(label_map, "w") as f:
        f.write("\\n".join(LABELS))
    print(f"Label map -> {label_map}")


if __name__ == "__main__":
    train()
"""

out = os.path.join(os.path.dirname(__file__), "train.py")
with open(out, "w") as f:
    f.write(content)
print(f"Wrote {len(content)} bytes to {out}")
