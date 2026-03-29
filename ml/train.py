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
