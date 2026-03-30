"""
DatasetLoader — loads skincare products from the CSV dataset.

CSV schema: id, product_name, category, brand, price, platform,
            product_url, ingredients, skin_type, concern, rating, image_url
"""
import logging
import os
import sys
from collections import defaultdict
from typing import ClassVar

import pandas as pd

from app.models import Product, ProductLinks

logger = logging.getLogger(__name__)

CONCERN_TAG_MAP: dict[str, str] = {
    "acne/pimples":                 "acne_pimples",
    "acne":                         "acne_pimples",
    "pimples":                      "acne_pimples",
    "blackheads":                   "blackheads_whiteheads",
    "blackheads/whiteheads":        "blackheads_whiteheads",
    "whiteheads":                   "blackheads_whiteheads",
    "dandruff":                     "dandruff",
    "dark circles":                 "dark_circles",
    "dark_circles":                 "dark_circles",
    "dark spots":                   "hyperpigmentation_dark_spots",
    "hyperpigmentation":            "hyperpigmentation_dark_spots",
    "hyperpigmentation/dark spots": "hyperpigmentation_dark_spots",
    "general_skincare":             "general_skincare",
}

PLATFORM_LINK_MAP: dict[str, str] = {
    "amazon":   "amazon",
    "flipkart": "flipkart",
    "nykaa":    "nykaa",
}

ALL_COUNTRIES = ["IN", "US", "UK", "CA", "AU", "DE", "FR", "JP"]


def _normalize_concern(raw: str) -> str:
    return CONCERN_TAG_MAP.get(raw.strip().lower(), "general_skincare")


def _build_links(platform: str, url: str) -> ProductLinks:
    links = ProductLinks(product_url=url or None)
    field = PLATFORM_LINK_MAP.get(platform.strip().lower())
    if field:
        setattr(links, field, url)
    return links


def _clean_str(val) -> str | None:
    s = str(val).strip()
    return None if s in ("", "nan", "NaN", "None") else s


class DatasetLoader:
    _products: ClassVar[list] = []
    _index: ClassVar[dict] = {}
    _loaded: ClassVar[bool] = False

    @classmethod
    def load(cls, csv_path: str = "data/skincare_products_clean.csv") -> None:
        if not os.path.exists(csv_path):
            logger.error("Products CSV not found: %s", csv_path)
            sys.exit(1)

        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            logger.error("Failed to read CSV: %s", e)
            sys.exit(1)

        products: list[Product] = []
        index: dict = defaultdict(list)

        for _, row in df.iterrows():
            try:
                name = _clean_str(row.get("product_name", ""))
                if not name:
                    continue

                product_id  = _clean_str(row.get("id", "")) or "0"
                brand       = _clean_str(row.get("brand", "")) or "Unknown"
                category    = _clean_str(row.get("category", "")) or ""
                platform    = _clean_str(row.get("platform", "")) or ""
                url         = _clean_str(row.get("product_url", "")) or ""
                ingredients = _clean_str(row.get("ingredients", "")) or ""
                concern_raw = _clean_str(row.get("concern", "")) or ""
                concern_tag = _normalize_concern(concern_raw)
                image_url   = _clean_str(row.get("image_url", ""))

                try:
                    price = float(str(row.get("price", "0")).replace(",", ""))
                except (ValueError, TypeError):
                    price = 0.0

                try:
                    rating = float(str(row.get("rating", "4.0")))
                except (ValueError, TypeError):
                    rating = 4.0

                product = Product(
                    product_id=f"P{product_id}",
                    name=name,
                    brand=brand,
                    price=price,
                    currency="INR",
                    rating=rating,
                    description=f"{category} — {ingredients[:120]}",
                    concern_tags=[concern_tag],
                    available_countries=ALL_COUNTRIES,
                    links=_build_links(platform, url),
                    image_url=image_url,
                )
                products.append(product)

                for country in ALL_COUNTRIES:
                    index[(concern_tag, country)].append(product)
                    index[("general_skincare", country)].append(product)

            except Exception as e:
                logger.warning("Skipping row: %s", e)

        cls._products = products
        cls._index = dict(index)
        cls._loaded = True
        logger.info(
            "Loaded %d products, %d index entries from %s",
            len(products), len(cls._index), csv_path,
        )

    @classmethod
    def get_index(cls) -> dict:
        return cls._index

    @classmethod
    def is_loaded(cls) -> bool:
        return cls._loaded

    @classmethod
    def record_count(cls) -> int:
        return len(cls._products)
