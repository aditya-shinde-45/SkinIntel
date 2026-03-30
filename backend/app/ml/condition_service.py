"""
ConditionDetectionService — single-model skin condition detection.

Path — Ollama vision model (llava-phi3 / llava / moondream):
    • One model detects: acne, dark_circles, hyperpigmentation,
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
import re
import threading

import requests as req

logger = logging.getLogger(__name__)

OLLAMA_URL          = os.environ.get("OLLAMA_URL", "http://localhost:11434")
CONDITION_THRESHOLD = float(os.environ.get("CONDITION_THRESHOLD", "0.20"))

_preferred_vision = os.environ.get("OLLAMA_VISION_MODEL", "moondream").strip()
_fallback_vision = [
    m.strip() for m in os.environ.get("OLLAMA_VISION_MODEL_FALLBACKS", "llava,moondream,llava:13b").split(",")
    if m.strip()
]
VISION_MODELS = list(dict.fromkeys([_preferred_vision] + _fallback_vision))

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

CONDITION_THRESHOLDS = {
    "acne": float(os.environ.get("CONDITION_THRESHOLD_ACNE", "0.08")),
    "dark_circles": float(os.environ.get("CONDITION_THRESHOLD_DARK_CIRCLES", "0.18")),
    "hyperpigmentation": float(os.environ.get("CONDITION_THRESHOLD_HYPERPIGMENTATION", "0.18")),
    "blackheads": float(os.environ.get("CONDITION_THRESHOLD_BLACKHEADS", "0.16")),
    "wrinkles": float(os.environ.get("CONDITION_THRESHOLD_WRINKLES", "0.16")),
    "oily_skin": float(os.environ.get("CONDITION_THRESHOLD_OILY_SKIN", "0.18")),
    "dry_skin": float(os.environ.get("CONDITION_THRESHOLD_DRY_SKIN", "0.18")),
}

FOCUSED_RESCUE_MARGIN = float(os.environ.get("CONDITION_FOCUSED_RESCUE_MARGIN", "0.06"))

CONDITION_PROMPT_HINTS = {
    "acne": "acne: inflamed pimples, papules, pustules, whiteheads, blackheads, or comedones",
    "dark_circles": "dark_circles: dark discoloration under the eyes (not lighting shadows)",
    "hyperpigmentation": "hyperpigmentation: dark patches or uneven skin tone on cheeks or forehead",
    "blackheads": "blackheads: visible dark clogged pores on nose/chin",
    "wrinkles": "wrinkles: visible lines or creases, especially forehead/crow's feet",
    "oily_skin": "oily_skin: overall facial shine and excess sebum",
    "dry_skin": "dry_skin: flaky, rough, tight, or dull dry areas",
}

CONDITION_KEY_ALIASES = {
    "dark_circles": "dark_circles",
    "dark_circle": "dark_circles",
    "dark under eyes": "dark_circles",
    "under_eye_darkness": "dark_circles",
    "hyperpigmentation": "hyperpigmentation",
    "hyper_pigmentation": "hyperpigmentation",
    "hyper pigmentation": "hyperpigmentation",
    "pigmentation": "hyperpigmentation",
    "uneven_tone": "hyperpigmentation",
    "blackheads": "blackheads",
    "blackhead": "blackheads",
    "wrinkles": "wrinkles",
    "wrinkle": "wrinkles",
    "fine_lines": "wrinkles",
    "oily_skin": "oily_skin",
    "dry_skin": "dry_skin",
    "acne": "acne",
    "pimple": "acne",
    "pimples": "acne",
    "breakout": "acne",
    "breakouts": "acne",
    "blemish": "acne",
    "blemishes": "acne",
    "comedone": "acne",
    "comedones": "acne",
}

class ConditionDetectionService:
    def __init__(self):
        self._vision_model = self._find_vision_model()

    # ── Setup ────────────────────────────────────────────────────────────────

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

        # Single vision model for all supported conditions
        vision_results = self._detect_via_vision(image_bytes)
        logger.info("Condition pass (broad) raw results: %s", vision_results)
        for condition, score in vision_results.items():
            threshold = CONDITION_THRESHOLDS.get(condition, CONDITION_THRESHOLD)
            if score >= threshold and condition not in detected:
                detected[condition] = min(score, 1.0)

        # Broad prompt can miss subtle conditions. Run one focused pass on only missing keys.
        missing_conditions = [c for c in DETECTABLE_CONDITIONS if c not in detected]
        if missing_conditions:
            focused_results = self._detect_missing_focused(image_bytes, missing_conditions)
            logger.info("Condition pass (focused) for %s raw results: %s", missing_conditions, focused_results)
            for condition, score in focused_results.items():
                threshold = CONDITION_THRESHOLDS.get(condition, CONDITION_THRESHOLD)
                if score >= threshold and condition not in detected:
                    detected[condition] = min(score, 1.0)
                    continue

                # Rescue near-threshold focused detections for subtle but visible conditions.
                rescue_floor = max(0.01, threshold - FOCUSED_RESCUE_MARGIN)
                if score >= rescue_floor and condition not in detected:
                    detected[condition] = min(score, 1.0)
                    logger.info(
                        "Condition rescue accepted: %s (score=%.3f, threshold=%.3f, rescue_floor=%.3f)",
                        condition,
                        score,
                        threshold,
                        rescue_floor,
                    )

        return [
            {
                "condition": cond,
                "confidence": round(conf, 4),
                "concern_tag": DETECTABLE_CONDITIONS.get(cond, cond),
            }
            for cond, conf in sorted(detected.items(), key=lambda x: -x[1])
        ]

    def is_available(self) -> bool:
        return self._vision_model is not None

    # ── Detection helpers ────────────────────────────────────────────────────

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
            "- Include conditions that are clearly visible; include mild but visible signs with lower confidence\n"
            "- Do not guess when uncertain\n"
            "- acne: inflamed pimples, papules, pustules, or comedones\n"
            "- dark_circles: dark discoloration UNDER the eyes (not shadows)\n"
            "- hyperpigmentation: dark patches or uneven skin tone on cheeks/forehead\n"
            "- blackheads: visible black dots on nose or chin\n"
            "- wrinkles: visible lines on forehead or around eyes\n"
            "- oily_skin: overall shine and excess sebum\n"
            "- dry_skin: flaky/rough texture and dull dry areas\n\n"
            "Return ONLY valid JSON using confidence scores between 0 and 1.\n"
            "Example:\n"
            '{"acne": 0.76, "dark_circles": 0.63, "wrinkles": 0.41}\n'
            "If nothing is clearly visible, respond: {}"
        )

        return self._run_vision_prompt(image_bytes, prompt)

    def _detect_missing_focused(self, image_bytes: bytes, missing_conditions: list[str]) -> dict[str, float]:
        if not missing_conditions:
            return {}

        hints = [CONDITION_PROMPT_HINTS[c] for c in missing_conditions if c in CONDITION_PROMPT_HINTS]
        keys = ", ".join(missing_conditions)

        prompt = (
            "You are a dermatology AI reviewing a facial photo for specific skin conditions only.\n"
            f"Evaluate only these keys: {keys}.\n"
            "Guidelines:\n"
            + "\n".join(f"- {h}" for h in hints)
            + "\nInclude subtle but visible signs too (do not require severe condition).\n"
            "Return ONLY valid JSON with confidence values from 0 to 1 for detected keys.\n"
            "Do not include keys outside the requested list.\n"
            "If none are clearly visible, return: {}"
        )

        return self._run_vision_prompt(image_bytes, prompt)

    def _run_vision_prompt(self, image_bytes: bytes, prompt: str) -> dict[str, float]:
        if self._vision_model is None:
            return {}

        b64 = base64.b64encode(image_bytes).decode("utf-8")

        try:
            with _ollama_lock:
                resp = req.post(
                    f"{OLLAMA_URL}/api/generate",
                    json={
                        "model": self._vision_model,
                        "format": "json",
                        "prompt": prompt,
                        "images": [b64],
                        "stream": False,
                        "options": {"temperature": 0.0, "num_predict": 60},
                    },
                    timeout=300,
                )

            if resp.status_code != 200:
                return {}

            raw = resp.json().get("response", "").strip()
            logger.debug("Vision response: %s", raw)

            if not raw:
                return {}

            start, end = raw.find("{"), raw.rfind("}") + 1
            if start == -1 or end == 0:
                return self._extract_from_text_response(raw)

            data = json.loads(raw[start:end])
            normalized = self._normalize_vision_result(data)
            if normalized:
                return normalized

            # If parsed JSON is empty but model returned explanatory text, try heuristic extraction.
            if raw not in {"{}", "{ }"}:
                return self._extract_from_text_response(raw)
            return {}

        except json.JSONDecodeError:
            logger.warning("Vision model JSON parse failed: %s", raw[:100])
            return {}
        except Exception as e:
            logger.warning("Vision detection failed: %s", e)
            return {}

    def _extract_from_text_response(self, raw: str) -> dict[str, float]:
        """
        Fallback for non-JSON responses: detect condition mentions in plain text.
        Assigns conservative confidence so thresholding still applies.
        """
        if not raw:
            return {}

        text = raw.lower()
        negation_pattern = re.compile(r"\b(no|not|none|without|absent)\b")
        if negation_pattern.search(text) and all(k not in text for k in ["acne", "pimple", "dark", "wrinkle", "pigment", "blackhead"]):
            return {}

        keyword_map = {
            "acne": ["acne", "pimple", "pimples", "breakout", "breakouts", "blemish", "comedone"],
            "dark_circles": ["dark circles", "dark circle", "under eye", "under-eye", "periorbital"],
            "hyperpigmentation": ["hyperpigmentation", "pigmentation", "dark patch", "uneven tone", "dark spots"],
            "blackheads": ["blackheads", "blackhead", "clogged pores"],
            "wrinkles": ["wrinkles", "wrinkle", "fine lines", "crow's feet"],
            "oily_skin": ["oily skin", "oily", "sebum", "shine"],
            "dry_skin": ["dry skin", "dry", "flaky", "rough", "tightness"],
        }

        detected: dict[str, float] = {}
        for condition, keywords in keyword_map.items():
            if any(k in text for k in keywords):
                if re.search(rf"\b(no|not|without)\s+({'|'.join(re.escape(k) for k in keywords[:2])})\b", text):
                    continue
                detected[condition] = 0.22

        if detected:
            logger.info("Condition text fallback extracted: %s", detected)
        return detected

    def _normalize_vision_result(self, data: dict) -> dict[str, float]:
        """
        Accepts varied model outputs and maps them to canonical condition keys.
        Supported value styles: true/false, yes/no, 0-1 confidence, 0-100 percent,
        or nested dicts like {"present": true, "confidence": 0.74}.
        """
        if not isinstance(data, dict):
            return {}

        normalized: dict[str, float] = {}
        for raw_key, raw_value in data.items():
            condition = self._normalize_condition_key(raw_key)
            if condition is None:
                continue

            score = self._value_to_score(raw_value)
            if score is None:
                continue

            if condition not in normalized or score > normalized[condition]:
                normalized[condition] = score

        return normalized

    def _normalize_condition_key(self, raw_key: object) -> str | None:
        if not isinstance(raw_key, str):
            return None

        key = raw_key.strip().lower().replace("-", "_").replace(" ", "_")
        if key in DETECTABLE_CONDITIONS:
            return key

        key_space = key.replace("_", " ")
        return CONDITION_KEY_ALIASES.get(key) or CONDITION_KEY_ALIASES.get(key_space)

    def _value_to_score(self, raw_value: object) -> float | None:
        if isinstance(raw_value, bool):
            return 0.80 if raw_value else None

        if isinstance(raw_value, (int, float)):
            if raw_value <= 0:
                return None
            if raw_value > 1.0:
                return min(float(raw_value) / 100.0, 1.0)
            return float(raw_value)

        if isinstance(raw_value, str):
            value = raw_value.strip().lower()
            if value in {"true", "yes", "present", "detected"}:
                return 0.80
            if value in {"false", "no", "absent", "none", "not_detected"}:
                return None
            try:
                num = float(value)
                if num <= 0:
                    return None
                if num > 1.0:
                    return min(num / 100.0, 1.0)
                return num
            except ValueError:
                return None

        if isinstance(raw_value, dict):
            present = raw_value.get("present")
            confidence = raw_value.get("confidence")

            if isinstance(confidence, (int, float)):
                conf = float(confidence)
                if conf > 1.0:
                    conf = min(conf / 100.0, 1.0)
                if isinstance(present, bool):
                    return conf if present else None
                return conf if conf > 0 else None

            if isinstance(present, bool):
                return 0.80 if present else None

        return None
