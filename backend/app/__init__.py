"""
Flask application factory for SkinIntel backend.
"""
import json
import logging
import time
import uuid

from flask import Flask, g, request
from flask_cors import CORS

from app.config import Config
from app.response import error_response

logger = logging.getLogger(__name__)


def create_app(config: Config | None = None) -> Flask:
    if config is None:
        config = Config.from_env()

    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = config.MAX_IMAGE_SIZE_MB * 1024 * 1024

    # ── CORS ────────────────────────────────────────────────────────────────
    CORS(app, origins=config.ALLOWED_ORIGIN)

    # ── Rate limiter ────────────────────────────────────────────────────────
    from app.middleware.rate_limiter import RateLimiter
    rate_limiter = RateLimiter(requests_per_minute=config.RATE_LIMIT_PER_MINUTE)

    @app.before_request
    def before():
        g.request_id = str(uuid.uuid4())
        g.start_time = time.time()
        result = rate_limiter.check()
        if result:
            return result

    @app.after_request
    def after(response):
        total_ms = round((time.time() - g.start_time) * 1000, 2)
        log_entry = {
            "request_id": g.get("request_id", ""),
            "method": request.method,
            "path": request.path,
            "status_code": response.status_code,
            "total_time_ms": total_ms,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        logger.info(json.dumps(log_entry))
        return response

    # ── Error handlers ──────────────────────────────────────────────────────
    @app.errorhandler(400)
    def bad_request(e):
        return error_response("validation_error", str(e), status_code=400)

    @app.errorhandler(413)
    def too_large(e):
        return error_response("image_too_large", "Uploaded file exceeds the size limit.", status_code=413)

    @app.errorhandler(415)
    def unsupported_media(e):
        return error_response("unsupported_media_type", str(e), status_code=415)

    @app.errorhandler(404)
    def not_found(e):
        return error_response("not_found", "The requested endpoint does not exist.", status_code=404)

    @app.errorhandler(405)
    def method_not_allowed(e):
        return error_response("method_not_allowed", str(e), status_code=405)

    @app.errorhandler(500)
    def internal_error(e):
        logger.error("Unhandled exception: %s", e)
        return error_response("internal_server_error", "An unexpected error occurred.", status_code=500)

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.exception("Unhandled exception")
        return error_response("internal_server_error", "An unexpected error occurred.", status_code=500)

    # ── Blueprints ──────────────────────────────────────────────────────────
    from app.controllers.analyze_controller import analyze_bp
    from app.controllers.health_controller import health_bp
    from app.controllers.products_controller import products_bp
    from app.controllers.auth_controller import auth_bp

    app.register_blueprint(analyze_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)

    # Ensure DynamoDB table exists (no-op if already created)
    try:
        from app.services.auth_service import ensure_table_exists
        ensure_table_exists()
    except Exception as e:
        logger.warning("DynamoDB table check failed (auth may not work): %s", e)

    return app
