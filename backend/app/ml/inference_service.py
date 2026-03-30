"""
InferenceService — skin concern CNN classification.

Uses the trained EfficientNetB0 concern model directly.
No LLM, no Ollama, no OpenAI.

Model output classes (sorted, matching training folder order):
  0: acne_pimples
  1: blackheads_whiteheads
  2: dandruff
  3: dark_circles
  4: hyperpigmentation_dark_spots
"""
import logging
import os

import numpy as np

from app.ml.model_loader import ModelLoader
from app.models import InferenceResult

logger = logging.getLogger(__name__)

LABELS = [
    "acne_pimples",
    "blackheads_whiteheads",
    "dandruff",
    "dark_circles",
    "hyperpigmentation_dark_spots",
]

STATIC_EXPLANATIONS: dict[str, str] = {
    "acne_pimples": (
        "Acne and pimples occur when hair follicles become clogged with oil and dead skin cells, "
        "leading to whiteheads, blackheads, or inflamed pimples. Hormonal changes, stress, and diet "
        "are common triggers. Use a gentle salicylic acid cleanser and a non-comedogenic moisturizer, "
        "and avoid touching your face."
    ),
    "blackheads_whiteheads": (
        "Blackheads and whiteheads are non-inflamed comedones caused by clogged pores. Blackheads "
        "oxidize and turn dark when exposed to air, while whiteheads stay closed under the skin. "
        "Regular exfoliation with BHA (salicylic acid) and keeping pores clean can help manage them."
    ),
    "dandruff": (
        "Dandruff is a common scalp condition causing flaking and mild itchiness, often linked to "
        "a yeast-like fungus, dry skin, or sensitivity to hair products. Use an anti-dandruff shampoo "
        "containing zinc pyrithione or ketoconazole, and maintain a consistent scalp care routine."
    ),
    "dark_circles": (
        "Dark circles under the eyes can result from genetics, lack of sleep, dehydration, or thin "
        "under-eye skin that reveals underlying blood vessels. Stay hydrated, get adequate sleep, and "
        "use an eye cream with caffeine or vitamin K to help reduce their appearance."
    ),
    "hyperpigmentation_dark_spots": (
        "Hyperpigmentation and dark spots are caused by excess melanin production, often triggered by "
        "sun exposure, acne scars, or hormonal changes. Apply broad-spectrum SPF 50 daily and consider "
        "serums with vitamin C, niacinamide, or alpha arbutin to gradually brighten affected areas."
    ),
}

CONFIDENCE_THRESHOLD = float(os.environ.get("CONFIDENCE_THRESHOLD", "0.40"))


class ModelInferenceError(Exception):
    pass


class InferenceService:
    def predict_raw(self, tensor: np.ndarray) -> dict:
        """Run CNN inference. Returns raw prediction dict."""
        try:
            model = ModelLoader.get_model()
            predictions = model.predict(tensor, verbose=0)
        except Exception as e:
            raise ModelInferenceError(f"Model inference failed: {e}") from e

        probs = predictions[0]
        idx = int(np.argmax(probs))
        label = LABELS[idx]
        confidence = float(probs[idx])
        return {"skin_type": label, "confidence": confidence, "probs": probs.tolist()}

    def build_result(self, raw: dict, conditions: list[dict]) -> InferenceResult:
        """Build InferenceResult from raw CNN output."""
        label      = raw["skin_type"]
        confidence = raw["confidence"]
        low_conf   = confidence < CONFIDENCE_THRESHOLD

        explanation = STATIC_EXPLANATIONS.get(label, STATIC_EXPLANATIONS["acne_pimples"])

        return InferenceResult(
            concern_label=label,
            confidence=confidence,
            low_confidence=low_conf,
            explanation=explanation,
            effective_concern="general_skincare" if low_conf else label,
        )

    def predict(self, tensor: np.ndarray, conditions: list[dict] | None = None) -> InferenceResult:
        return self.build_result(self.predict_raw(tensor), conditions or [])
