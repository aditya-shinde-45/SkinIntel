"""
InferenceService — skin type CNN classification + Ollama LLM explanation.

Model output classes (alphabetical, matching training folder order):
  0: combination  1: dry  2: normal  3: oily

LLM priority:
  1. Ollama (local, free) — OLLAMA_URL + OLLAMA_MODEL env vars
  2. OpenAI              — OPENAI_API_KEY env var
  3. Static fallback     — always works, no dependencies
"""
import logging
import os
import threading

import numpy as np

from app.ml.model_loader import ModelLoader
from app.models import InferenceResult

logger = logging.getLogger(__name__)

LABELS = ["combination", "dry", "normal", "oily"]

SKIN_TYPE_TO_CONCERN: dict[str, str] = {
    "combination": "combination_skin",
    "dry":         "dry_skin",
    "normal":      "normal_skin",
    "oily":        "oily_skin",
}

STATIC_EXPLANATIONS: dict[str, str] = {
    "combination": (
        "Combination skin has an oily T-zone (forehead, nose, chin) with normal or dry cheeks. "
        "It's one of the most common skin types, influenced by genetics, hormones, and climate. "
        "Balance it with a gentle gel cleanser and a lightweight moisturizer — avoid heavy creams on the T-zone."
    ),
    "dry": (
        "Dry skin produces less sebum than normal, leading to tightness, flakiness, and a dull complexion. "
        "Cold weather, hot showers, harsh cleansers, and aging all strip the skin's natural moisture barrier. "
        "Restore it with a ceramide-rich moisturizer, hyaluronic acid serum, and a creamy, sulfate-free cleanser."
    ),
    "normal": (
        "Normal skin is well-balanced — not too oily or too dry — with small pores and minimal imperfections. "
        "It's the result of good genetics and a healthy skin barrier, but still needs daily care to stay that way. "
        "Keep it glowing with a gentle cleanser, daily SPF 50, and a vitamin C serum."
    ),
    "oily": (
        "Oily skin produces excess sebum from overactive sebaceous glands, causing shine, enlarged pores, "
        "and a higher tendency toward acne and blackheads. Hormonal changes, genetics, and humidity are common triggers. "
        "Manage it with a foaming cleanser, niacinamide serum, and a lightweight oil-free moisturizer."
    ),
}

CONFIDENCE_THRESHOLD = float(os.environ.get("CONFIDENCE_THRESHOLD", "0.40"))

# Ollama config — defaults work if Ollama is running locally
OLLAMA_URL   = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "mistral")

# Shared lock — imported by condition_service too so both respect it
from app.ml.condition_service import _ollama_lock


class ModelInferenceError(Exception):
    pass


class InferenceService:
    def __init__(self):
        self._llm_backend = self._detect_llm_backend()

    def _detect_llm_backend(self) -> str:
        """Return 'ollama', 'openai', or 'static'. Auto-starts Ollama if installed."""
        import requests as req

        if self._ensure_ollama_running():
            try:
                r = req.get(f"{OLLAMA_URL}/api/tags", timeout=3)
                if r.status_code == 200:
                    available = [m["name"] for m in r.json().get("models", [])]
                    base = OLLAMA_MODEL.split(":")[0]
                    match = next((m for m in available if m.startswith(base)), None)
                    if match:
                        logger.info("LLM backend: Ollama (%s)", match)
                        return "ollama"
                    else:
                        logger.warning(
                            "Ollama running but model '%s' not pulled. "
                            "Run: ollama pull %s", OLLAMA_MODEL, OLLAMA_MODEL,
                        )
            except Exception as e:
                logger.warning("Ollama health check failed: %s", e)

        if os.environ.get("OPENAI_API_KEY"):
            logger.info("LLM backend: OpenAI")
            return "openai"

        logger.info("LLM backend: static (install Ollama + run: ollama pull mistral)")
        return "static"

    def _ensure_ollama_running(self) -> bool:
        """Check if Ollama is up; if not, try to start it as a background process."""
        import subprocess
        import time
        import requests as req

        # Already up?
        try:
            if req.get(f"{OLLAMA_URL}/api/tags", timeout=2).status_code == 200:
                return True
        except Exception:
            pass

        # Try to launch it
        try:
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            logger.info("Launched Ollama server in background — waiting up to 5s...")
            for _ in range(5):
                time.sleep(1)
                try:
                    if req.get(f"{OLLAMA_URL}/api/tags", timeout=1).status_code == 200:
                        logger.info("Ollama is now reachable.")
                        return True
                except Exception:
                    pass
        except FileNotFoundError:
            logger.info("Ollama not installed. Get it at https://ollama.com")
        except Exception as e:
            logger.warning("Could not start Ollama: %s", e)

        return False

    def _ollama_explain(self, skin_type: str, confidence: float, conditions: list[dict]) -> str | None:
        try:
            import requests as req
            prompt = _build_prompt(skin_type, confidence, conditions)
            with _ollama_lock:
                r = req.post(
                    f"{OLLAMA_URL}/api/generate",
                    json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False,
                          "options": {"temperature": 0.7, "num_predict": 180}},
                    timeout=120,
                )
            if r.status_code == 200:
                return r.json().get("response", "").strip()
        except Exception as e:
            logger.warning("Ollama request failed: %s", e)
        return None

    def _openai_explain(self, skin_type: str, confidence: float, conditions: list[dict]) -> str | None:
        try:
            import openai
            client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": _build_prompt(skin_type, confidence, conditions)}],
                max_tokens=250,
                temperature=0.7,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            logger.warning("OpenAI request failed: %s", e)
        return None

    def _get_explanation(self, skin_type: str, confidence: float, conditions: list[dict]) -> str:
        """Get LLM explanation covering skin type + detected conditions."""
        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
        with ThreadPoolExecutor(max_workers=1) as ex:
            if self._llm_backend == "ollama":
                fut = ex.submit(self._ollama_explain, skin_type, confidence, conditions)
            elif self._llm_backend == "openai":
                fut = ex.submit(self._openai_explain, skin_type, confidence, conditions)
            else:
                return _build_static_explanation(skin_type, conditions)

            try:
                result = fut.result(timeout=60)
                return result or _build_static_explanation(skin_type, conditions)
            except (FuturesTimeout, Exception) as e:
                logger.warning("LLM explanation timed out (%s) — using static.", e)
                return _build_static_explanation(skin_type, conditions)

    def predict_raw(self, tensor: np.ndarray) -> dict:
        """Run CNN only — no LLM. Returns raw prediction dict."""
        try:
            model = ModelLoader.get_model()
            predictions = model.predict(tensor, verbose=0)
        except Exception as e:
            raise ModelInferenceError(f"Model inference failed: {e}") from e

        probs = predictions[0]
        idx = int(np.argmax(probs))
        skin_type = LABELS[idx]
        confidence = float(probs[idx])
        return {"skin_type": skin_type, "confidence": confidence, "probs": probs.tolist()}

    def build_result(self, raw: dict, conditions: list[dict]) -> InferenceResult:
        """Build InferenceResult from raw CNN output + conditions, calling LLM for explanation."""
        skin_type  = raw["skin_type"]
        confidence = raw["confidence"]

        low_confidence = confidence < CONFIDENCE_THRESHOLD
        concern_label  = SKIN_TYPE_TO_CONCERN.get(skin_type, "normal_skin")
        effective_concern = "general_skincare" if low_confidence else concern_label

        explanation = self._get_explanation(skin_type, confidence, conditions)

        return InferenceResult(
            concern_label=skin_type,
            confidence=confidence,
            low_confidence=low_confidence,
            explanation=explanation,
            effective_concern=effective_concern,
        )

    def predict(self, tensor: np.ndarray, conditions: list[dict] | None = None) -> InferenceResult:
        """Convenience method: CNN + LLM in one call."""
        return self.build_result(self.predict_raw(tensor), conditions or [])


def _build_prompt(skin_type: str, confidence: float, conditions: list[dict]) -> str:
    condition_names = [c["condition"].replace("_", " ") for c in conditions]

    base = (
        f"You are a friendly dermatologist AI assistant for SkinIntel. "
        f"A CNN model analyzed a facial photo and detected '{skin_type}' skin type "
        f"with {confidence * 100:.1f}% confidence."
    )

    if condition_names:
        conditions_str = ", ".join(condition_names)
        return (
            f"{base} Additionally, the following skin conditions were detected: {conditions_str}. "
            f"Write 3-4 warm, concise sentences: (1) describe the {skin_type} skin type, "
            f"(2) briefly mention the detected conditions and what causes them, "
            f"(3) give one practical skincare tip that addresses both the skin type and conditions. "
            f"Be reassuring and non-alarming. Plain text only, no bullet points or markdown."
        )

    return (
        f"{base} "
        f"Write exactly 3 sentences: (1) what {skin_type} skin is, "
        f"(2) what causes or characterizes it, "
        f"(3) one practical skincare tip. "
        f"Be warm, concise, and non-alarming. Plain text only, no markdown."
    )


def _build_static_explanation(skin_type: str, conditions: list[dict]) -> str:
    base = STATIC_EXPLANATIONS.get(skin_type, STATIC_EXPLANATIONS["normal"])
    if not conditions:
        return base

    condition_names = [c["condition"].replace("_", " ") for c in conditions]
    conditions_str = ", ".join(condition_names)
    return (
        f"{base} "
        f"Additionally, our AI detected the following skin concerns: {conditions_str}. "
        f"Consider targeted treatments for these alongside your regular skincare routine."
    )
