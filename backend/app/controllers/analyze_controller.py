"""
AnalyzeController — POST /api/v1/analyze

Flow:
  1. Preprocess uploaded image
  2. Run concern CNN → top predicted skin concern + confidence
  3. Fetch product recommendations for that concern
"""
import logging
import time

from flask import Blueprint, request

from app.config import Config
from app.ml.condition_service import ConditionDetectionService
from app.ml.inference_service import InferenceService, ModelInferenceError
from app.middleware.auth_middleware import require_auth
from app.response import error_response, success_response
from app.services.image_preprocessor import ImagePreprocessorError, ImagePreprocessorService
from app.services.recommendation_service import RecommendationService

logger = logging.getLogger(__name__)

analyze_bp = Blueprint("analyze", __name__)

SUPPORTED_COUNTRIES = {"IN", "US", "UK", "CA", "AU", "DE", "FR", "JP"}

_inference_service      = InferenceService()
_condition_service      = ConditionDetectionService()
_recommendation_service = RecommendationService()


def _get_preprocessor() -> ImagePreprocessorService:
    config = Config.from_env()
    return ImagePreprocessorService(max_size_mb=config.MAX_IMAGE_SIZE_MB)


@analyze_bp.post("/api/v1/analyze")
@require_auth
def analyze():
    total_start = time.time()
    config = Config.from_env()

    # ── Validate inputs ──────────────────────────────────────────────────────
    country = request.form.get("country", "").strip().upper()
    if not country or country not in SUPPORTED_COUNTRIES:
        return error_response(
            "invalid_country",
            f"'country' must be one of: {', '.join(sorted(SUPPORTED_COUNTRIES))}",
            status_code=400,
        )

    try:
        min_price = float(request.form.get("min_price", ""))
        max_price = float(request.form.get("max_price", ""))
    except (ValueError, TypeError):
        return error_response("validation_error", "'min_price' and 'max_price' must be numeric.", status_code=400)

    if min_price > max_price:
        return error_response("invalid_price_range", "'min_price' must be <= 'max_price'.", status_code=400)

    limit  = min(int(request.form.get("limit", 10)), 50)
    offset = max(int(request.form.get("offset", 0)), 0)

    # ── Preprocess image ─────────────────────────────────────────────────────
    preprocessor = _get_preprocessor()
    image_file = request.files.get("image")
    image_url  = request.form.get("image_url", "").strip()

    try:
        if image_file:
            raw_bytes = image_file.read()
            image_file.seek(0)
            tensor = preprocessor.preprocess_file(image_file)
        elif image_url:
            raw_bytes = preprocessor._fetch_with_retry(image_url)
            tensor = preprocessor._decode_and_normalize(raw_bytes)
        else:
            return error_response("validation_error", "Provide 'image' file or 'image_url'.", status_code=400)
    except ImagePreprocessorError as e:
        return error_response(e.error_code, str(e), status_code=e.status_code)

    # ── CNN inference ────────────────────────────────────────────────────────
    inference_start = time.time()
    try:
        conditions = _condition_service.detect(raw_bytes)
    except Exception as e:
        logger.error("Condition detection failed: %s", e)
        return error_response("model_inference_failed", str(e), status_code=500)

    inference_time_ms = (time.time() - inference_start) * 1000

    # Build result from top condition
    if conditions:
        top = conditions[0]
        raw = {"skin_type": top["condition"], "confidence": top["confidence"], "probs": []}
    else:
        # Fallback: run inference_service directly on tensor
        try:
            raw = _inference_service.predict_raw(tensor)
        except ModelInferenceError as e:
            logger.error("Inference failed: %s", e)
            return error_response("model_inference_failed", str(e), status_code=500)

    result = _inference_service.build_result(raw, conditions)

    # ── Product recommendations ──────────────────────────────────────────────
    concern = result.effective_concern
    rec = _recommendation_service.get_recommendations(
        concern=concern,
        country=country,
        min_price=min_price,
        max_price=max_price,
        limit=limit,
        offset=offset,
    )

    total_time_ms = (time.time() - total_start) * 1000

    data = {
        "skin_concern":   result.concern_label,
        "confidence":     round(result.confidence, 4),
        "low_confidence": result.low_confidence,
        "explanation":    result.explanation,
        "conditions":     conditions,
        "products":       [_serialize_product(p) for p in rec.products],
        "no_results":     rec.no_results,
        "concern_label":  result.concern_label,
    }

    meta = {
        "model_version":     config.MODEL_VERSION,
        "inference_time_ms": round(inference_time_ms, 2),
        "total_time_ms":     round(total_time_ms, 2),
        "total_count":       rec.total_count,
        "limit":             limit,
        "offset":            offset,
        "conditions_detected": len(conditions),
    }

    return success_response(data, meta=meta)


def _serialize_product(p) -> dict:
    return {
        "product_id":          p.product_id,
        "name":                p.name,
        "brand":               p.brand,
        "price":               p.price,
        "currency":            p.currency,
        "rating":              p.rating,
        "description":         p.description,
        "concern_tags":        p.concern_tags,
        "available_countries": p.available_countries,
        "image_url":           p.image_url,
        "links": {
            "amazon":      p.links.amazon,
            "nykaa":       p.links.nykaa,
            "flipkart":    p.links.flipkart,
            "product_url": p.links.product_url,
        },
    }
