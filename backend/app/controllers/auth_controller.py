"""
AuthController — POST /api/v1/auth/register, POST /api/v1/auth/login
"""
import logging
from flask import Blueprint, request
from app.response import error_response, success_response
from app.services.auth_service import AuthService, AuthError

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__)
_auth_service = AuthService()


@auth_bp.post("/api/v1/auth/register")
def register():
    data = request.get_json(silent=True) or {}
    full_name = data.get("full_name", "").strip()
    email     = data.get("email", "").strip()
    password  = data.get("password", "")
    country   = data.get("country", "").strip().upper()

    if not all([full_name, email, password, country]):
        return error_response("validation_error", "full_name, email, password, and country are required.", 400)
    if len(password) < 6:
        return error_response("validation_error", "Password must be at least 6 characters.", 400)

    try:
        result = _auth_service.register(full_name, email, password, country)
        return success_response(result, status_code=201)
    except AuthError as e:
        return error_response("auth_error", str(e), status_code=e.status_code)


@auth_bp.post("/api/v1/auth/login")
def login():
    data = request.get_json(silent=True) or {}
    email    = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return error_response("validation_error", "email and password are required.", 400)

    try:
        result = _auth_service.login(email, password)
        return success_response(result)
    except AuthError as e:
        return error_response("auth_error", str(e), status_code=e.status_code)
