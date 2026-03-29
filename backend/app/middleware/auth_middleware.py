"""
JWT auth middleware — require_auth decorator for protected routes.
"""
import functools
from flask import request, g
from app.response import error_response
from app.services.auth_service import AuthService, AuthError

_auth_service = AuthService()


def require_auth(fn):
    """Decorator that validates Bearer JWT and sets g.user."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return error_response("unauthorized", "Authentication required. Please log in.", 401)
        token = auth_header[7:]
        try:
            g.user = _auth_service.verify_token(token)
        except AuthError as e:
            return error_response("unauthorized", str(e), e.status_code)
        return fn(*args, **kwargs)
    return wrapper
