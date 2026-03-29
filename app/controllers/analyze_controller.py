"""
AnalyzeController — POST /api/v1/analyze

Runs three tasks concurrently via ThreadPoolExecutor:
  1. Skin type CNN (trained)          → oily / dry / normal / combination
  2. Condition detection (HF + vision) → acne / dark_circles / hyperpigmentation / etc.
  3. LLM explanation (Ollama/static)  → runs inside InferenceService.predict()

Total latency ≈ max(CNN, vision) instead of CNN + vision + LLM summed.
"""
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FuturesTimeout

from flask import Blueprint, request

from app.config import Config
from app.ml.inference_service import InferenceService, ModelInferenceError
from app.ml.condition_service import ConditionDetectionService
from app.response import error_response, success_response
from app.services.image_preprocessor import ImagePreprocessorError, ImagePreprocessorService
from app.services.recommendation_service import RecommendationService

logger = logging.getLogger(__name__)

analyze_bp = Blueprint("analyze", __name__)

SUPPORTED_COUNTRIES = {"IN", "US", "UK", "CA", "AU", "DE", "FR", "JP"}

_inference_service      = InferenceService()
_condition_service      = ConditionDetectionService()
_recommendation_service = RecommendationService()
_executor               = ThreadPoolExecutor(max_workers=3, thread_name_prefix="analyze")


def _get_preprocessor() -> ImagePreprocessorService:
    config = Config.from_env()
    return ImagePreprocessorService(max_size_mb=config.MAX_IMAGE_SIZE_MB)


@analyze_bp.post("/api/v1/analyze")
def analyze():
    total_start = time.time()
    config = Config.from_env()

    # ── Validate inputs ─────────────────────────────────────────────────────
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

    # ── Get raw image bytes ─────────────────────────────────────────────────
    preprocessor = _get_preprocessor()
    image_file = request.files.get("image")
    image_url  = request.form.get("image_url", "").strip()

    try:
        if image_file:
            raw_bytes = image_file.read()
            image_file.seek(0)                          # reset for MIME check
            tensor = preprocessor.preprocess_file(image_file)
        elif image_url:
            raw_bytes = preprocessor._fetch_with_retry(image_url)
            tensor = preprocessor._decode_and_normalize(raw_bytes)
        else:
            return error_response("validation_error", "Provide 'image' file or 'image_url'.", status_code=400)
    except ImagePreprocessorError as e:
        return error_response(e.error_code, str(e), status_code=e.status_code)

    # ── Run CNN inference (fast, no Ollama) ─────────────────────────────────
    inference_start = time.time()
    try:
        # Get raw CNN prediction without LLM explanation yet
        skin_result_raw = _executor.submit(_inference_service.predict_raw, tensor)
        skin_result_raw = skin_result_raw.result(timeout=30)
    except FuturesTimeout:
        return error_response("request_timeout", "Skin type inference timed out.", status_code=504)
    except ModelInferenceError as e:
        logger.error("Skin type inference failed: %s", e)
        return error_response("model_inference_failed", str(e), status_code=500)

    inference_time_ms = (time.time() - inference_start) * 1000

    # ── Condition detection (vision LLM — sequential with explanation) ───────
    try:
        conditions = _condition_service.detect(raw_bytes)
    except Exception as e:
        logger.warning("Condition detection failed (non-fatal): %s", e)
        conditions = []

    # ── LLM explanation (uses conditions for richer text) ────────────────────
    skin_result = _inference_service.build_result(skin_result_raw, conditions)

    # ── Build combined concern list ──────────────────────────────────────────
    # Primary: skin type concern (from trained model)
    primary_concern = skin_result.effective_concern

    # Secondary: detected conditions (from pretrained model), deduplicated
    condition_concerns = [c["concern_tag"] for c in conditions if c["concern_tag"] != primary_concern]

    # All unique concerns to fetch products for
    all_concerns = [primary_concern] + condition_concerns

    # ── Get products for each concern ────────────────────────────────────────
    concern_products = {}
    for concern in all_concerns:
        rec = _recommendation_service.get_recommendations(
            concern=concern,
            country=country,
            min_price=min_price,
            max_price=max_price,
            limit=limit,
            offset=offset,
        )
        if not rec.no_results:
            concern_products[concern] = {
                "products": [_serialize_product(p) for p in rec.products],
                "total_count": rec.total_count,
            }

    # Primary products (for backward compat)
    primary_rec = concern_products.get(primary_concern, {"products": [], "total_count": 0})

    total_time_ms = (time.time() - total_start) * 1000

    data = {
        # Skin type result (Model 1)
        "skin_type":      skin_result.concern_label,
        "confidence":     round(skin_result.confidence, 4),
        "low_confidence": skin_result.low_confidence,
        "explanation":    skin_result.explanation,

        # Detected conditions (Model 2)
        "conditions": conditions,

        # Products for primary skin type
        "products":   primary_rec["products"],
        "no_results": len(primary_rec["products"]) == 0,

        # Products grouped by concern (skin type + all conditions)
        "products_by_concern": concern_products,

        # Legacy field for backward compat
        "concern_label": skin_result.concern_label,
    }

    meta = {
        "model_version":    config.MODEL_VERSION,
        "inference_time_ms": round(inference_time_ms, 2),
        "total_time_ms":    round(total_time_ms, 2),
        "total_count":      primary_rec["total_count"],
        "limit":            limit,
        "offset":           offset,
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
            "amazon":   p.links.amazon,
            "nykaa":    p.links.nykaa,
            "flipkart": p.links.flipkart,
        },
    }
