"""
Standard response envelope helpers for SkinIntel backend.

Every HTTP response from the API uses the shape:
{
    "success": bool,
    "data": dict | list | None,
    "error": {"code": str, "message": str} | None,
    "meta": {
        "request_id": str,
        "timestamp": str,   # ISO 8601
        ...                 # endpoint-specific fields
    }
}
"""
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from flask import jsonify


def _build_meta(extra_meta: Optional[dict] = None) -> dict:
    """Build the base meta object, merging any extra fields."""
    meta = {
        "request_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if extra_meta:
        meta.update(extra_meta)
    return meta


def success_response(data: Any, meta: Optional[dict] = None, status_code: int = 200):
    """
    Return a Flask JSON response with success=True.

    :param data:        The payload to place in the ``data`` field.
    :param meta:        Optional dict of extra fields merged into ``meta``.
    :param status_code: HTTP status code (default 200).
    """
    body = {
        "success": True,
        "data": data,
        "error": None,
        "meta": _build_meta(meta),
    }
    return jsonify(body), status_code


def error_response(code: str, message: str, meta: Optional[dict] = None, status_code: int = 400):
    """
    Return a Flask JSON response with success=False.

    :param code:        Machine-readable error code string (e.g. ``"validation_error"``).
    :param message:     Human-readable description of the error.
    :param meta:        Optional dict of extra fields merged into ``meta``.
    :param status_code: HTTP status code (default 400).
    """
    body = {
        "success": False,
        "data": None,
        "error": {
            "code": code,
            "message": message,
        },
        "meta": _build_meta(meta),
    }
    return jsonify(body), status_code
