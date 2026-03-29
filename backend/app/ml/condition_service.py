"""
ConditionDetectionService — dual-path skin condition detection.

Path 1 — HuggingFace CNN models (fast, offline after first download):
  • imfarzanansari/skintelligent-acne  → acne severity levels

Path 2 — Ollama vision model (llava / llava-phi3 / moondream):
  • Visually inspects the image and detects: dark_circles, hyperpigmentation,
    blackheads, wrinkles, oily_skin, dry_skin
  • Falls back gracefully if no vision model is available

Pull a vision model once:
  ollama pull llava          (~4.7 GB, best quality)
  ollama pull llava-phi3     (~2.9 GB, faster)
  ollama pull moondream      (~1.7 GB, lightest)
"""
import base64
import json
import logging
import os
import threading
from io import BytesIO

import requests as req

logger = logging.getLogger(__name__)

OLLAMA_URL          = os.environ.get("OLLAMA_URL", "http://localhost:11434")
CONDITION_THRESHOLD = float(os.environ.get("CONDITION_THRESHOLD", "0.20"))
VISION_MODELS       = ["llava-phi3", "llava", "moondream", "llava:13b"]

# Global lock — Ollama handles one request at a time on CPU
_ollama_lock = threading.Lock()

DETECTABLE_CONDITIONS = {
    "acne":              "acne",
    "dark_circles":      "dark_circles",
    "hyperpigmentation": "hyperpigmentation",
    "blackheads":        "blackheads",
    "wrinkles":          "wrinkles",
    "oily_skin":         "oily_skin",
    "dry_skin":          "dry_skin",
}

# Acne model label map (lowercase as model outputs)
ACNE_LABEL_MAP = {
    "level -1": None,
    "level 0":  None,
    "level 1":  "acne",
    "level 2":  "acne",
    "level 3":  "acne",
    "level 4":  "acne",
}


class ConditionDetectionService:
    def __init__(self):
        self._acne_pipe = self._load_acne_model()
        self._vision_model = self._find_vision_model()

    # ── Setup ────────────────────────────────────────────────────────────────

    def _load_acne_model(self):
        try:
            from transformers import pipeline as hf_pipeline
            pipe = hf_pipeline(
                "image-classification",
                model="imfarzanansari/skintelligent-acne",
                device=-1,
                top_k=None,
            )
            logger.info("Loaded acne detection model.")
            return pipe
        except Exception as e:
            logger.warning("Could not load acne model: %s", e)
            return None

    def _find_vision_model(self) -> str | None:
        """Return the first Ollama vision model that is pulled locally."""
        try:
            r = req.get(f"{OLLAMA_URL}/api/tags", timeout=3)
            if r.status_code != 200:
                return None
            available = [m["name"] for m in r.json().get("models", [])]
            for candidate in VISION_MODELS:
                base = candidate.split(":")[0]
                match = next((m for m in available if m.startswith(base)), None)
                if match:
                    logger.info("Vision model for condition detection: %s", match)
                    return match
            logger.info(
                "No vision model found. For dark circles / hyperpigmentation detection run: "
                "ollama pull llava-phi3"
            )
        except Exception:
            pass
        return None

    # ── Public API ───────────────────────────────────────────────────────────

    def detect(self, image_bytes: bytes) -> list[dict]:
        """
        Returns list of detected conditions sorted by confidence desc:
        [{"condition": "dark_circles", "confidence": 0.85, "concern_tag": "dark_circles"}, ...]
        """
        detected: dict[str, float] = {}

        # Path 1: CNN acne model
        acne_score = self._detect_acne(image_bytes)
        if acne_score >= CONDITION_THRESHOLD:
            detected["acne"] = min(acne_score, 1.0)

        # Path 2: Vision LLM for everything else
        vision_results = self._detect_via_vision(image_bytes)
        for condition, score in vision_results.items():
            if score >= CONDITION_THRESHOLD and condition not in detected:
                detected[condition] = min(score, 1.0)

        return [
            {
                "condition": cond,
                "confidence": round(conf, 4),
                "concern_tag": DETECTABLE_CONDITIONS.get(cond, cond),
            }
            for cond, conf in sorted(detected.items(), key=lambda x: -x[1])
        ]

    def is_available(self) -> bool:
        return self._acne_pipe is not None or self._vision_model is not None

    # ── Detection helpers ────────────────────────────────────────────────────

    def _detect_acne(self, image_bytes: bytes) -> float:
        if self._acne_pipe is None:
            return 0.0
        try:
            from PIL import Image
            img = Image.open(BytesIO(image_bytes)).convert("RGB")
            results = self._acne_pipe(img)
            return sum(
                float(r["score"])
                for r in results
                if ACNE_LABEL_MAP.get(r["label"].lower().strip()) == "acne"
            )
        except Exception as e:
            logger.warning("Acne detection failed: %s", e)
            return 0.0

    def _detect_via_vision(self, image_bytes: bytes) -> dict[str, float]:
        """
        Ask the vision LLM one question covering all conditions at once.
        Uses a lock so only one Ollama request runs at a time.
        """
        if self._vision_model is None:
            return {}

        b64 = base64.b64encode(image_bytes).decode("utf-8")

        prompt = (
            "You are a dermatology AI. Look carefully at this facial photo. "
            "Check ONLY for these conditions and answer with a JSON object.\n"
            "Rules:\n"
            "- Only include a condition if it is CLEARLY and OBVIOUSLY visible\n"
            "- Do NOT guess or assume — if unsure, leave it out\n"
            "- dark_circles: dark discoloration UNDER the eyes (not shadows)\n"
            "- hyperpigmentation: dark patches or uneven skin tone on cheeks/forehead\n"
            "- blackheads: visible black dots on nose or chin\n"
            "- wrinkles: visible lines on forehead or around eyes\n\n"
            "Respond with ONLY a JSON object, example:\n"
            '{"dark_circles": true, "blackheads": true}\n'
            "If nothing is clearly visible, respond: {}"
        )

        try:
            with _ollama_lock:
                resp = req.post(
                    f"{OLLAMA_URL}/api/generate",
                    json={
                        "model": self._vision_model,
                        "prompt": prompt,
                        "images": [b64],
                        "stream": False,
                        "options": {"temperature": 0.0, "num_predict": 60},
                    },
                    timeout=90,
                )

            if resp.status_code != 200:
                return {}

            raw = resp.json().get("response", "").strip()
            logger.debug("Vision response: %s", raw)

            start, end = raw.find("{"), raw.rfind("}") + 1
            if start == -1 or end == 0:
                return {}

            data = json.loads(raw[start:end])
            return {
                k: 0.80
                for k, v in data.items()
                if k in DETECTABLE_CONDITIONS and v is True
            }

        except json.JSONDecodeError:
            logger.warning("Vision model JSON parse failed: %s", raw[:100])
            return {}
        except Exception as e:
            logger.warning("Vision detection failed: %s", e)
            return {}
