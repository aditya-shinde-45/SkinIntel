"""
WSGI entry point for Gunicorn.
Loads .env, model, and dataset before creating the Flask app.
"""
import logging
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

from app.config import Config
from app.data.dataset_loader import DatasetLoader
from app.ml.model_loader import ModelLoader
from app import create_app

config = Config.from_env()
ModelLoader.load(config.MODEL_PATH)
DatasetLoader.load(config.PRODUCTS_CSV_PATH)

app = create_app(config)
