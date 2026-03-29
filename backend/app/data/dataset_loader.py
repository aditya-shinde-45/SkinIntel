"""
DatasetLoader — loads real skincare products from the CSV dataset.
Maps product_type → concern_tags and generates store search URLs.
"""
import logging
import os
import re
import sys
from collections import defaultdict
from typing import ClassVar

import pandas as pd

from app.models import Product, ProductLinks

logger = logging.getLogger(__name__)

# Map CSV product_type → concern tags
TYPE_TO_CONCERNS: dict[str, list[str]] = {
    "Moisturiser": ["dry_skin", "normal_skin", "combination_skin", "general_skincare"],
    "Cleanser":    ["oily_skin", "acne", "normal_skin", "general_skincare"],
    "Serum":       ["hyperpigmentation", "dark_circles", "wrinkles", "general_skincare"],
    "Eye Care":    ["dark_circles", "wrinkles"],
    "Toner":       ["oily_skin", "blackheads", "combination_skin"],
    "Exfoliator":  ["blackheads", "hyperpigmentation", "oily_skin"],
    "Mask":        ["oily_skin", "blackheads", "acne", "dry_skin"],
    "Peel":        ["hyperpigmentation", "blackheads", "wrinkles"],
    "Oil":         ["dry_skin", "normal_skin"],
    "Mist":        ["dry_skin", "normal_skin", "general_skincare"],
    "Balm":        ["dry_skin", "general_skincare"],
    "Body Wash":   ["general_skincare"],
    "Bath Salts":  ["general_skincare"],
    "Bath Oil":    ["dry_skin", "general_skincare"],
}

# Ingredient keywords → additional concern tags
INGREDIENT_CONCERN_MAP = {
    "salicylic":      ["acne", "blackheads", "oily_skin"],
    "benzoyl":        ["acne"],
    "retinol":        ["wrinkles", "acne"],
    "retinoid":       ["wrinkles", "acne"],
    "niacinamide":    ["oily_skin", "hyperpigmentation", "acne"],
    "vitamin c":      ["hyperpigmentation", "dark_circles"],
    "ascorbic":       ["hyperpigmentation"],
    "kojic":          ["hyperpigmentation"],
    "arbutin":        ["hyperpigmentation", "dark_circles"],
    "tranexamic":     ["hyperpigmentation"],
    "glycolic":       ["hyperpigmentation", "blackheads"],
    "lactic acid":    ["hyperpigmentation", "dry_skin"],
    "hyaluronic":     ["dry_skin", "normal_skin"],
    "ceramide":       ["dry_skin", "normal_skin"],
    "caffeine":       ["dark_circles"],
    "peptide":        ["wrinkles", "dark_circles"],
    "collagen":       ["wrinkles"],
    "zinc":           ["acne", "oily_skin"],
}

ALL_COUNTRIES = ["IN", "US", "UK", "CA", "AU", "DE", "FR", "JP"]

PRODUCT_IMAGES = {
    "Moisturiser": "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400",
    "Cleanser":    "https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?w=400",
    "Serum":       "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=400",
    "Eye Care":    "https://images.unsplash.com/photo-1617897903246-719242758050?w=400",
    "Toner":       "https://images.unsplash.com/photo-1556228724-4f1836f8f7fd?w=400",
    "Exfoliator":  "https://images.unsplash.com/photo-1629198735660-e39ea93f5c18?w=400",
    "Mask":        "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=400",
    "Peel":        "https://images.unsplash.com/photo-1631214524020-6f3f80c5ea1d?w=400",
    "Oil":         "https://images.unsplash.com/photo-1570194065650-d99fb4bedf0a?w=400",
    "Mist":        "https://images.unsplash.com/photo-1526758097130-bab247274f58?w=400",
    "Balm":        "https://images.unsplash.com/photo-1608248597279-f99d160bfcbc?w=400",
    "default":     "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400",
}


def _parse_price_gbp(price_str: str) -> float:
    """Extract numeric price from strings like '£5.20', '£22.00'."""
    try:
        return float(re.sub(r"[^\d.]", "", str(price_str)))
    except (ValueError, TypeError):
        return 0.0


def _gbp_to_inr(gbp: float) -> float:
    """Approximate GBP → INR conversion (1 GBP ≈ 107 INR)."""
    return round(gbp * 107, 0)


def _build_links(product_url: str) -> ProductLinks:
    """Use the actual dataset URL as the buy link."""
    return ProductLinks(
        amazon=None,
        nykaa=None,
        flipkart=None,
        product_url=product_url if product_url and product_url != "nan" else None,
    )


def _get_concerns(product_type: str, ingredients_str: str) -> list[str]:
    concerns = set(TYPE_TO_CONCERNS.get(product_type, ["general_skincare"]))
    ingreds_lower = str(ingredients_str).lower()
    for keyword, extra_concerns in INGREDIENT_CONCERN_MAP.items():
        if keyword in ingreds_lower:
            concerns.update(extra_concerns)
    return list(concerns)


def _extract_brand(product_name: str) -> str:
    """Best-effort brand extraction from product name."""
    known_brands = [
        "The Ordinary", "CeraVe", "La Roche-Posay", "Neutrogena", "Olay",
        "Clinique", "Estee Lauder", "Kiehl's", "Origins", "Dermalogica",
        "Paula's Choice", "First Aid Beauty", "Drunk Elephant", "Sunday Riley",
        "Tatcha", "Glow Recipe", "Herbivore", "Pixi", "Mario Badescu",
        "Peter Thomas Roth", "Murad", "Perricone MD", "REN", "Elemis",
        "Clarins", "Lancome", "Shiseido", "SK-II", "Laneige", "Innisfree",
        "COSRX", "Some By Mi", "Minimalist", "Plum", "Mamaearth", "WOW",
        "Biotique", "Himalaya", "Lotus", "Garnier", "L'Oreal", "Nivea",
        "Pond's", "Vaseline", "Dove", "Cetaphil", "Bioderma", "Avene",
        "Vichy", "Uriage", "Nuxe", "Caudalie", "Weleda",
    ]
    name_lower = product_name.lower()
    for brand in known_brands:
        if brand.lower() in name_lower:
            return brand
    # Fall back to first word(s)
    words = product_name.split()
    return words[0] if words else "Unknown"


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

        for i, row in df.iterrows():
            try:
                name = str(row["product_name"]).strip()
                if not name or name == "nan":
                    continue

                product_type = str(row.get("product_type", "")).strip()
                ingredients  = str(row.get("clean_ingreds", ""))
                price_gbp    = _parse_price_gbp(row.get("price", "0"))
                price_inr    = _gbp_to_inr(price_gbp)
                product_url  = str(row.get("product_url", ""))
                brand        = _extract_brand(name)
                concerns     = _get_concerns(product_type, ingredients)
                image        = str(row.get("image_url", "")).strip() or PRODUCT_IMAGES.get(product_type, PRODUCT_IMAGES["default"])

                product = Product(
                    product_id=f"CSV{i:04d}",
                    name=name,
                    brand=brand,
                    price=price_inr,
                    currency="INR",
                    rating=round(4.0 + (i % 10) * 0.1, 1),  # 4.0–4.9 spread
                    description=f"{product_type} — {name}",
                    concern_tags=concerns,
                    available_countries=ALL_COUNTRIES,
                    links=_build_links(product_url),
                    image_url=image,
                )
                products.append(product)

                for concern in concerns:
                    for country in ALL_COUNTRIES:
                        index[(concern, country)].append(product)

            except Exception as e:
                logger.warning("Skipping row %d: %s", i, e)

        cls._products = products
        cls._index = dict(index)
        cls._loaded = True
        logger.info("Loaded %d products, %d index entries from %s", len(products), len(cls._index), csv_path)

    @classmethod
    def get_index(cls) -> dict:
        return cls._index

    @classmethod
    def is_loaded(cls) -> bool:
        return cls._loaded

    @classmethod
    def record_count(cls) -> int:
        return len(cls._products)
