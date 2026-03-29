"""
Evaluate the trained SkinIntel skin-type model.

Usage:
  MODEL_PATH=models/model.keras \
  DATA_DIR=/home/ideabliss/Downloads/archive/skin_type_classification_dataset \
  python3 ml/evaluate.py
"""
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator

LABELS    = ["combination", "dry", "normal", "oily"]
IMG_SIZE  = (224, 224)
BATCH_SIZE = 32


def evaluate():
    model_path = os.environ.get("MODEL_PATH", "models/model.keras")
    data_dir   = os.environ.get("DATA_DIR", "dataset")
    split      = os.environ.get("SPLIT", "valid")   # valid | test

    model = tf.keras.models.load_model(model_path)
    print(f"Loaded: {model_path}")

    datagen = ImageDataGenerator(rescale=1.0 / 255)
    gen = datagen.flow_from_directory(
        os.path.join(data_dir, split),
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        classes=LABELS,
        shuffle=False,
    )

    loss, acc = model.evaluate(gen, verbose=1)
    print(f"\nOverall — Accuracy: {acc:.4f}  Loss: {loss:.4f}")

    preds  = model.predict(gen, verbose=0)
    y_pred = np.argmax(preds, axis=1)
    y_true = gen.classes

    print("\nPer-class accuracy:")
    for i, label in enumerate(LABELS):
        mask = y_true == i
        if mask.sum() > 0:
            class_acc = (y_pred[mask] == i).mean()
            print(f"  {label:<12} {class_acc:.4f}  ({mask.sum()} samples)")

    print("\nConfusion matrix (rows=true, cols=predicted):")
    header = "         " + "  ".join(f"{l[:5]:>5}" for l in LABELS)
    print(header)
    for i, true_label in enumerate(LABELS):
        row = [str((y_pred[y_true == i] == j).sum()).rjust(5) for j in range(len(LABELS))]
        print(f"{true_label:<8} " + "  ".join(row))


if __name__ == "__main__":
    evaluate()
