"""
Configuration dataclass for SkinIntel backend.
All values are read from environment variables with documented defaults.
"""
import os
from dataclasses import dataclass, field


@dataclass
class Config:
    # Path to the trained Keras model file (.keras)
    MODEL_PATH: str = field(default_factory=lambda: os.environ.get("MODEL_PATH", "models/model.keras"))

    # Semantic version string for the active model, included in every analyze response
    MODEL_VERSION: str = field(default_factory=lambda: os.environ.get("MODEL_VERSION", "1.0.0"))

    # Path to the skincare products CSV dataset
    PRODUCTS_CSV_PATH: str = field(default_factory=lambda: os.environ.get("PRODUCTS_CSV_PATH", "data/products.csv"))

    # CORS allowed origin; defaults to wildcard (all origins)
    ALLOWED_ORIGIN: str = field(default_factory=lambda: os.environ.get("ALLOWED_ORIGIN", "*"))

    # Maximum accepted image upload size in megabytes
    MAX_IMAGE_SIZE_MB: int = field(default_factory=lambda: int(os.environ.get("MAX_IMAGE_SIZE_MB", "10")))

    # Port the Flask/Gunicorn server listens on
    PORT: int = field(default_factory=lambda: int(os.environ.get("PORT", "5000")))

    # Runtime environment: dev | staging | prod
    ENV: str = field(default_factory=lambda: os.environ.get("ENV", "dev"))

    # Per-IP sliding-window rate limit (requests per minute) for /api/v1/analyze
    RATE_LIMIT_PER_MINUTE: int = field(default_factory=lambda: int(os.environ.get("RATE_LIMIT_PER_MINUTE", "30")))

    # Minimum softmax confidence required before falling back to general_skincare
    CONFIDENCE_THRESHOLD: float = field(default_factory=lambda: float(os.environ.get("CONFIDENCE_THRESHOLD", "0.40")))

    @classmethod
    def from_env(cls) -> "Config":
        """Construct a Config instance populated entirely from environment variables."""
        return cls()
