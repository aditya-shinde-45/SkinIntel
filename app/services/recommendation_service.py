"""
RecommendationService — filters and ranks products from the in-memory index.
"""
from app.data.dataset_loader import DatasetLoader
from app.models import Product, RecommendationResult


class RecommendationService:
    def get_recommendations(
        self,
        concern: str,
        country: str,
        min_price: float,
        max_price: float,
        limit: int = 10,
        offset: int = 0,
    ) -> RecommendationResult:
        index = DatasetLoader.get_index()

        candidates = index.get((concern, country), [])
        filtered = self._filter_by_price(candidates, min_price, max_price)

        # Fallback to general_skincare if no results
        if not filtered and concern != "general_skincare":
            candidates = index.get(("general_skincare", country), [])
            filtered = self._filter_by_price(candidates, min_price, max_price)

        if not filtered:
            return RecommendationResult(products=[], total_count=0, no_results=True)

        sorted_products = sorted(filtered, key=lambda p: p.rating, reverse=True)
        total_count = len(sorted_products)
        page = sorted_products[offset: offset + limit]

        return RecommendationResult(products=page, total_count=total_count, no_results=False)

    @staticmethod
    def _filter_by_price(products: list, min_price: float, max_price: float) -> list:
        return [p for p in products if min_price <= p.price <= max_price]
