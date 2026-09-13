"""
Gemini integration (Phase 7).

Gemini is an explanation layer only. It receives the already-verified AI
context, returns plain-language JSON, and that JSON is validated against
``AIExplanationResponse``. It never decides or mutates business truth.

Transport is the Gemini REST API through the already-installed ``httpx``
client, so no extra SDK is added and the client stays easy to replace or
mock. Credentials come from ``GEMINI_API_KEY``; the model from
``GEMINI_MODEL`` (default ``gemini-2.0-flash``).

Failure policy: Gemini is optional. Any failure (missing key, timeout,
HTTP error, malformed/empty response) is converted into
``AIExplanationResponse(ai_available=False)`` and never raised into the
deterministic pipeline. One attempt per call, no retries; 15s timeout.
"""

import json
import os
from typing import Optional

import httpx

from app.contracts.ai_context import (
    AIBusinessBriefContext,
    AIInsightContext,
    AIRecommendationContext,
)
from app.contracts.api import AIExplanationResponse
from app.core.errors import GeminiError

_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
_DEFAULT_MODEL = "gemini-2.0-flash"
_TIMEOUT_SECONDS = 15.0

_SYSTEM_INSTRUCTION = (
    "You explain verified inventory facts to a small shop owner in simple, "
    "friendly language. The provided context is the only source of truth. "
    "Never invent or guess numbers, dates, shipments, quantities, prices, or "
    "product details. Never change, replace, or second-guess the given "
    "recommendation action or reorder quantity; explain them exactly as "
    "given. If a value is null it is unavailable: say so and do not assume "
    "zero. Do not claim to know anything that is not in the context. Reply "
    "only with the requested JSON."
)

_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "reason": {"type": "string"},
        "action_explanation": {"type": "string"},
        "future_note": {"type": "string"},
    },
    "required": ["summary"],
    "propertyOrdering": ["summary", "reason", "action_explanation", "future_note"],
}


def explain_recommendation(context: AIRecommendationContext) -> AIExplanationResponse:
    """Explain a product recommendation from verified context."""
    return _explain(
        "Explain the following verified product recommendation to the shop owner. "
        "The action and reorder quantity are final decisions; explain them.\n"
        f"Verified context: {context.model_dump_json()}"
    )


def generate_business_brief(context: AIBusinessBriefContext) -> AIExplanationResponse:
    """Summarize the verified business condition for the dashboard."""
    return _explain(
        "Summarize the following verified business condition for the shop owner. "
        "Use only the supplied counts and values.\n"
        f"Verified context: {context.model_dump_json()}"
    )


def generate_insight(context: AIInsightContext) -> AIExplanationResponse:
    """Explain verified analytics trends for the analytics page."""
    return _explain(
        "Explain the following verified demand trends for the shop owner. "
        "Do not forecast and do not add analytics that are not provided.\n"
        f"Verified context: {context.model_dump_json()}"
    )


def _explain(user_prompt: str) -> AIExplanationResponse:
    """Run one Gemini call and validate its output; never raise outward."""
    try:
        data = _generate(user_prompt)
        return _validate(data)
    except GeminiError:
        return AIExplanationResponse(ai_available=False)
    except Exception:  # unexpected failure must not break deterministic flow
        return AIExplanationResponse(ai_available=False)


def _generate(user_prompt: str) -> dict:
    """Call Gemini once and return parsed JSON. Isolated for testing."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise GeminiError("GEMINI_API_KEY is not configured")
    model = os.environ.get("GEMINI_MODEL", _DEFAULT_MODEL)
    payload = {
        "systemInstruction": {"parts": [{"text": _SYSTEM_INSTRUCTION}]},
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": _RESPONSE_SCHEMA,
            "temperature": 0.2,
        },
    }
    try:
        response = httpx.post(
            f"{_API_BASE}/{model}:generateContent",
            params={"key": api_key},
            json=payload,
            timeout=_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise GeminiError("Gemini request timed out", details={"reason": "timeout"}) from exc
    except httpx.HTTPStatusError as exc:
        raise GeminiError(
            "Gemini returned an error status",
            details={"status": exc.response.status_code},
        ) from exc
    except httpx.HTTPError as exc:
        raise GeminiError("Gemini request failed", details={"reason": "connection"}) from exc

    try:
        text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise GeminiError("Gemini response was empty or malformed") from exc
    try:
        return json.loads(text)
    except (TypeError, ValueError) as exc:
        raise GeminiError("Gemini response was not valid JSON") from exc


def _validate(data: dict) -> AIExplanationResponse:
    """Validate Gemini JSON against AIExplanationResponse; fail closed."""
    if not isinstance(data, dict):
        raise GeminiError("Gemini response was not an object")
    summary = data.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        raise GeminiError("Gemini response was missing a summary")
    return AIExplanationResponse(
        summary=summary,
        reason=_optional_str(data, "reason"),
        action_explanation=_optional_str(data, "action_explanation"),
        future_note=_optional_str(data, "future_note"),
        ai_available=True,
    )


def _optional_str(data: dict, key: str) -> Optional[str]:
    value = data.get(key)
    return value if isinstance(value, str) and value.strip() else None
