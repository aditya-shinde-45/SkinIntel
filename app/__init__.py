from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.response import success_response


def create_app() -> Flask:
	"""Build and configure the Flask application."""
	config = Config.from_env()

	app = Flask(__name__)
	app.config["MAX_CONTENT_LENGTH"] = config.MAX_IMAGE_SIZE_MB * 1024 * 1024

	CORS(app, origins=config.ALLOWED_ORIGIN)

	@app.get("/health")
	def health():
		return success_response(
			{
				"service": "skinintel-backend",
				"status": "ok",
				"environment": config.ENV,
				"model_version": config.MODEL_VERSION,
			}
		)

	return app
