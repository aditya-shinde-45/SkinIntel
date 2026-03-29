"""
Core data model dataclasses for SkinIntel backend.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ProductLinks:
    """Purchase links for a skincare product."""
    amazon: Optional[str] = None
    nykaa: Optional[str] = None
    flipkart: Optional[str] = None
    product_url: Optional[str] = None  # direct product page URL from dataset


@dataclass
class Product:
    """A single skincare product record loaded from the dataset."""
    product_id: str
    name: str
    brand: str
    price: float
    currency: str
    rating: float
    description: str
    concern_tags: list  # list[str]
    available_countries: list  # list[str]
    links: ProductLinks = field(default_factory=ProductLinks)
    image_url: Optional[str] = None


@dataclass
class InferenceResult:
    """Output produced by InferenceService.predict()."""
    concern_label: str          # One of the 8 supported concern labels
    confidence: float           # Softmax probability in [0.0, 1.0]
    low_confidence: bool        # True iff confidence < CONFIDENCE_THRESHOLD
    explanation: str            # Human-readable description of the concern
    effective_concern: str      # concern_label, or "general_skincare" when low_confidence


@dataclass
class RecommendationResult:
    """Output produced by RecommendationService.get_recommendations()."""
    products: list              # list[Product]
    total_count: int            # Total matching products before pagination
    no_results: bool = False    # True when no products matched even after fallback
