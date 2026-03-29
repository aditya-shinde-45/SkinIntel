"""
DatasetLoader — loads and indexes the skincare products CSV at startup.
"""
import logging
import sys
from collections import defaultdict
from typing import ClassVar

import pandas as pd

from app.models import Product, ProductLinks

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = {
    "product_id", "name", "brand", "price", "currency",
    "rating", "description", "concern_tags", "available_countries",
    "links_amazon", "links_nykaa", "links_flipkart",
}

OPTIONAL_COLUMNS = {"image_url"}


class DatasetLoader:
    _products: ClassVar[list] = []
    _index: ClassVar[dict] = {}
    _loaded: ClassVar[bool] = False

    @classmethod
    def load(cls, csv_path: str) -> None:
        try:
            df = pd.read_csv(csv_path)
        except FileNotFoundError:
            logger.error("Products CSV not found: %s", csv_path)
            sys.exit(1)

        # Warn on unexpected columns
        actual = set(df.columns)
        unexpected = actual - REQUIRED_COLUMNS - OPTIONAL_COLUMNS
        if unexpected:
            logger.warning("Unexpected CSV columns (ignored): %s", unexpected)

        missing = REQUIRED_COLUMNS - actual
        if missing:
            logger.error("CSV is missing required columns: %s", missing)
            sys.exit(1)

        products: list[Product] = []
        index: dict = defaultdict(list)

        for i, row in df.iterrows():
            try:
                concern_tags = [t.strip() for t in str(row["concern_tags"]).split(",") if t.strip()]
                available_countries = [c.strip() for c in str(row["available_countries"]).split(",") if c.strip()]

                product = Product(
                    product_id=str(row["product_id"]),
                    name=str(row["name"]),
                    brand=str(row["brand"]),
                    price=float(row["price"]),
                    currency=str(row["currency"]),
                    rating=float(row["rating"]),
                    description=str(row["description"]),
                    concern_tags=concern_tags,
                    available_countries=available_countries,
                    links=ProductLinks(
                        amazon=str(row["links_amazon"]) if pd.notna(row["links_amazon"]) else None,
                        nykaa=str(row["links_nykaa"]) if pd.notna(row["links_nykaa"]) else None,
                        flipkart=str(row["links_flipkart"]) if pd.notna(row["links_flipkart"]) else None,
                    ),
                    image_url=str(row["image_url"]) if "image_url" in row and pd.notna(row.get("image_url")) else None,
                )
                products.append(product)

                for concern in concern_tags:
                    for country in available_countries:
                        index[(concern, country)].append(product)

            except (KeyError, ValueError, TypeError) as e:
                logger.warning("Skipping record at index %d: %s", i, e)

        cls._products = products
        cls._index = dict(index)
        cls._loaded = True
        logger.info("Loaded %d products, %d index entries", len(products), len(cls._index))

    @classmethod
    def get_index(cls) -> dict:
        return cls._index

    @classmethod
    def is_loaded(cls) -> bool:
        return cls._loaded

    @classmethod
    def record_count(cls) -> int:
        return len(cls._products)
