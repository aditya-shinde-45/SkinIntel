"""
ConditionDetectionService — CNN-based skin concern classifier.

Uses the trained EfficientNetB0 model to detect one of 5 skin concerns:
  acne_pimples, blackheads_whiteheads, dandruff, dark_circles,
  hyperpigmentation_dark_spots

No LLM or external API required.
"""
import logging
import threading

import numpy as np
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__)

# Matches the sorted folder names used during training
CONCERN_LABELS = [
    "acne_pimples",
    "blackheads_whiteheads",
    "dandruff",
    "dark_circles",
    "hyperpigmentation_dark_spots",
]

# Maps model output label → concern_tag used by recommendation service
LABEL_TO_CONCERN_TAG: dict[str, str] = {
    "acne_pimples":                  "acne_pimples",
    "blackheads_whiteheads":         "blackheads_whiteheads",
    "dandruff":                      "dandruff",
    "dark_circles":                  "dark_circles",
    "hyperpigmentation_dark_spots":  "hyperpigmentation_dark_spots",
}

IMG_SIZE = (224, 224)

# Shared lock so only one inference runs at a time (CPU safety)
_ollama_lock = threading.Lock()  # kept same name for import compat in inference_service


class ConditionDetectionService:
    def __init__(self):
        self._model = None
        self._load_model()

    def _load_model(self):
        import os
        import tensorflow as tf

        model_path = os.environ.get("CONCERN_MODEL_PATH", "models/skin_concern_model.keras")
        if not os.path.exists(model_path):
            logger.warning(
                "Concern model not found at '%s'. "
                "Run ml/train.py to train it. Condition detection disabled.",
                model_path,
            )
            return
        try:
            self._model = tf.keras.models.load_model(model_path)
            logger.info("Concern CNN loaded from %s", model_path)
        except Exception as e:
            logger.error("Failed to load concern model: %s", e)

    def is_available(self) -> bool:
        return self._model is not None

    def detect(self, image_bytes: bytes) -> list[dict]:
        """
        Returns a list with the top predicted skin concern:
        [{"condition": "acne_pimples", "confidence": 0.87, "concern_tag": "acne_pimples"}]
        Returns [] if model is not loaded.
        """
        if self._model is None:
            return []

        try:
            tensor = self._preprocess(image_bytes)
            with _ollama_lock:
                preds = self._model.predict(tensor, verbose=0)

            probs = preds[0]
            idx = int(np.argmax(probs))
            label = CONCERN_LABELS[idx]
            confidence = float(probs[idx])

            logger.info("Concern CNN: %s (%.3f)", label, confidence)

            return [{
                "condition":   label,
                "confidence":  round(confidence, 4),
                "concern_tag": LABEL_TO_CONCERN_TAG.get(label, label),
            }]

        except Exception as e:
            logger.error("Condition detection failed: %s", e)
            return []

    def _preprocess(self, image_bytes: bytes) -> np.ndarray:
        img = Image.open(BytesIO(image_bytes)).convert("RGB")
        img = img.resize(IMG_SIZE, Image.LANCZOS)
        # EfficientNetB0 expects raw [0, 255] — no normalization needed
        arr = np.array(img, dtype=np.float32)
        return np.expand_dims(arr, axis=0)
