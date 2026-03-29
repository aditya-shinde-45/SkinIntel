"""
HealthController — GET /api/v1/health
"""
import os

from flask import Blueprint

from app.data.dataset_loader import DatasetLoader
from app.ml.model_loader import ModelLoader
from app.response import success_response

health_bp = Blueprint("health", __name__)


@health_bp.get("/api/v1/health")
def health():
    return success_response({
        "status": "ok",
        "model_loaded": ModelLoader.is_loaded(),
        "dataset_loaded": DatasetLoader.is_loaded(),
        "model_version": os.environ.get("MODEL_VERSION", "1.0.0"),
        "dataset_record_count": DatasetLoader.record_count(),
    })
