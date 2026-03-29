"""
AuthService — user registration, login, JWT tokens, DynamoDB storage.

DynamoDB table: skinintel_users
  PK: email (string)
  Attributes: user_id, full_name, email, password_hash, country, created_at
"""
import logging
import os
import uuid
from datetime import datetime, timezone, timedelta

import bcrypt
import boto3
import jwt
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

TABLE_NAME  = os.environ.get("DYNAMODB_TABLE", "skinintel_users")
JWT_SECRET  = os.environ.get("JWT_SECRET", "skinintel-dev-secret-change-in-prod")
JWT_EXPIRY_HOURS = int(os.environ.get("JWT_EXPIRY_HOURS", "24"))
AWS_REGION  = os.environ.get("AWS_REGION", "ap-south-1")


def _dynamo_kwargs() -> dict:
    """Build boto3 kwargs, always preferring env vars over ~/.aws/credentials."""
    kwargs = {"region_name": AWS_REGION}
    endpoint = os.environ.get("DYNAMODB_ENDPOINT") or None
    if endpoint:
        kwargs["endpoint_url"] = endpoint
    # Explicitly pass credentials from env if set, so ~/.aws/credentials is ignored
    key_id = os.environ.get("AWS_ACCESS_KEY_ID")
    secret  = os.environ.get("AWS_SECRET_ACCESS_KEY")
    if key_id and secret:
        kwargs["aws_access_key_id"]     = key_id
        kwargs["aws_secret_access_key"] = secret
    return kwargs


def _get_table():
    dynamodb = boto3.resource("dynamodb", **_dynamo_kwargs())
    return dynamodb.Table(TABLE_NAME)


def ensure_table_exists():
    """Create the DynamoDB table if it doesn't exist."""
    dynamodb = boto3.resource("dynamodb", **_dynamo_kwargs())
    try:
        table = dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[{"AttributeName": "email", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "email", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        table.wait_until_exists()
        logger.info("Created DynamoDB table '%s'.", TABLE_NAME)
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "ResourceInUseException":
            logger.info("DynamoDB table '%s' already exists.", TABLE_NAME)
        elif code == "AccessDeniedException":
            # Table likely already exists, CreateTable just isn't permitted
            logger.info("No CreateTable permission — assuming table '%s' exists.", TABLE_NAME)
        else:
            logger.error("Could not create DynamoDB table: %s", e)
            raise


class AuthError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


class AuthService:

    def register(self, full_name: str, email: str, password: str, country: str) -> dict:
        email = email.lower().strip()
        table = _get_table()

        # Check duplicate
        try:
            resp = table.get_item(Key={"email": email})
            if resp.get("Item"):
                raise AuthError("An account with this email already exists.", 409)
        except ClientError as e:
            logger.error("DynamoDB error: %s", e)
            raise AuthError("Database error. Please try again.", 500)

        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        item = {
            "email":         email,
            "user_id":       user_id,
            "full_name":     full_name.strip(),
            "password_hash": password_hash,
            "country":       country.upper(),
            "created_at":    now,
        }

        try:
            table.put_item(Item=item)
        except ClientError as e:
            logger.error("DynamoDB put_item error: %s", e)
            raise AuthError("Could not create account. Please try again.", 500)

        logger.info("Registered user: %s", email)
        token = self._generate_token(user_id, email, full_name, country)
        return {"token": token, "user": self._safe_user(item)}

    def login(self, email: str, password: str) -> dict:
        email = email.lower().strip()
        table = _get_table()

        try:
            resp = table.get_item(Key={"email": email})
            item = resp.get("Item")
        except ClientError as e:
            logger.error("DynamoDB error: %s", e)
            raise AuthError("Database error. Please try again.", 500)

        if not item:
            raise AuthError("Invalid email or password.", 401)

        if not bcrypt.checkpw(password.encode(), item["password_hash"].encode()):
            raise AuthError("Invalid email or password.", 401)

        logger.info("Login: %s", email)
        token = self._generate_token(
            item["user_id"], email, item["full_name"], item["country"]
        )
        return {"token": token, "user": self._safe_user(item)}

    def verify_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthError("Session expired. Please log in again.", 401)
        except jwt.InvalidTokenError:
            raise AuthError("Invalid token.", 401)

    def _generate_token(self, user_id: str, email: str, full_name: str, country: str) -> str:
        payload = {
            "user_id":   user_id,
            "email":     email,
            "full_name": full_name,
            "country":   country,
            "exp":       datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS),
        }
        return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    @staticmethod
    def _safe_user(item: dict) -> dict:
        return {
            "user_id":    item["user_id"],
            "full_name":  item["full_name"],
            "email":      item["email"],
            "country":    item["country"],
            "created_at": item.get("created_at", ""),
        }
