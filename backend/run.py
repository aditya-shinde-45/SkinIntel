"""
SkinIntel backend startup script.
Loads model + dataset, then starts Flask/Gunicorn.
"""
import logging
import os

# Load .env FIRST — before any boto3/AWS imports pick up ~/.aws/credentials
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv optional; use real env vars in production

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

from app.config import Config
from app.data.dataset_loader import DatasetLoader
from app.ml.model_loader import ModelLoader
from app import create_app

config = Config.from_env()

# Load model (exits on failure)
ModelLoader.load(config.MODEL_PATH)

# Load dataset (exits on failure)
DatasetLoader.load(config.PRODUCTS_CSV_PATH)

app = create_app(config)

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=config.PORT,
        debug=(config.ENV == "dev"),
        use_reloader=False,   # prevent double model load on startup
    )
