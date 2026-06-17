"""
Configuration dataclass for SkinIntel backend.
All values are read from environment variables with documented defaults.
"""
import os
from pathlib import Path
from dataclasses import dataclass, field


def _resolve_existing_path(raw_path: str) -> str:
    path = Path(raw_path).expanduser()
    if path.exists():
        return str(path)

    app_root = Path(__file__).resolve().parents[2]
    basename = path.name

    candidates = []
    if not path.is_absolute():
        candidates.extend([
            app_root / path,
            app_root / "backend" / path,
        ])

    candidates.extend([
        app_root / "models" / basename,
        app_root / "backend" / "models" / basename,
        app_root / "data" / basename,
        app_root / "backend" / "data" / basename,
    ])

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    return raw_path


@dataclass
class Config:
    # Path to the trained Keras model file (.keras)
    MODEL_PATH: str = field(default_factory=lambda: os.environ.get("MODEL_PATH") or "models/model.keras")

    # Semantic version string for the active model, included in every analyze response
    MODEL_VERSION: str = field(default_factory=lambda: os.environ.get("MODEL_VERSION", "1.0.0"))

    # Path to the skincare products CSV dataset
    PRODUCTS_CSV_PATH: str = field(default_factory=lambda: os.environ.get("PRODUCTS_CSV_PATH") or "data/products.csv")

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
        config = cls()
        config.MODEL_PATH = _resolve_existing_path(config.MODEL_PATH)
        config.PRODUCTS_CSV_PATH = _resolve_existing_path(config.PRODUCTS_CSV_PATH)
        return config
