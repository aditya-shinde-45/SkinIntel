"""
ModelLoader — singleton that loads and holds the Keras CNN model in memory.
"""
import logging
import sys
from typing import ClassVar, Optional

logger = logging.getLogger(__name__)


class ModelLoader:
    _model: ClassVar[Optional[object]] = None

    @classmethod
    def load(cls, model_path: str) -> None:
        import os
        import tensorflow as tf  # lazy import to keep startup fast if not needed

        if not os.path.exists(model_path):
            logger.error("Model file not found: %s", model_path)
            sys.exit(1)

        try:
            cls._model = tf.keras.models.load_model(model_path)
            logger.info("Model loaded from %s", model_path)
        except Exception as e:
            logger.error("Failed to load model: %s", e)
            sys.exit(1)

    @classmethod
    def get_model(cls):
        if cls._model is None:
            raise RuntimeError("Model is not loaded. Call ModelLoader.load() first.")
        return cls._model

    @classmethod
    def is_loaded(cls) -> bool:
        return cls._model is not None
