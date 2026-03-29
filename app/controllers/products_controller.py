"""
ProductsController — GET /api/v1/products
"""
from flask import Blueprint, request

from app.response import error_response, success_response
from app.services.recommendation_service import RecommendationService

products_bp = Blueprint("products", __name__)

SUPPORTED_COUNTRIES = {"IN", "US", "UK", "CA", "AU", "DE", "FR", "JP"}
SUPPORTED_CONCERNS = {"oily_skin", "dry_skin", "normal_skin", "combination_skin", "general_skincare"}

_recommendation_service = RecommendationService()


@products_bp.get("/api/v1/products")
def get_products():
    concern = request.args.get("concern", "").strip()
    country = request.args.get("country", "").strip().upper()

    if not concern or concern not in SUPPORTED_CONCERNS:
        return error_response(
            "validation_error",
            f"'concern' must be one of: {', '.join(sorted(SUPPORTED_CONCERNS))}",
            status_code=400,
        )

    if not country or country not in SUPPORTED_COUNTRIES:
        return error_response(
            "invalid_country",
            f"'country' must be one of: {', '.join(sorted(SUPPORTED_COUNTRIES))}",
            status_code=400,
        )

    try:
        min_price = float(request.args.get("min_price", 0))
        max_price = float(request.args.get("max_price", 99999))
    except (ValueError, TypeError):
        return error_response(
            "validation_error",
            "'min_price' and 'max_price' must be numeric.",
            status_code=400,
        )

    if min_price > max_price:
        return error_response(
            "invalid_price_range",
            "'min_price' must be <= 'max_price'.",
            status_code=400,
        )

    limit = min(int(request.args.get("limit", 10)), 50)
    offset = max(int(request.args.get("offset", 0)), 0)

    rec = _recommendation_service.get_recommendations(
        concern=concern,
        country=country,
        min_price=min_price,
        max_price=max_price,
        limit=limit,
        offset=offset,
    )

    data = {
        "products": [
            {
                "product_id": p.product_id,
                "name": p.name,
                "brand": p.brand,
                "price": p.price,
                "currency": p.currency,
                "rating": p.rating,
                "description": p.description,
                "concern_tags": p.concern_tags,
                "available_countries": p.available_countries,
                "links": {
                    "amazon": p.links.amazon,
                    "nykaa": p.links.nykaa,
                    "flipkart": p.links.flipkart,
                },
            }
            for p in rec.products
        ],
        "no_results": rec.no_results,
    }

    meta = {
        "total_count": rec.total_count,
        "limit": limit,
        "offset": offset,
    }

    return success_response(data, meta=meta)
