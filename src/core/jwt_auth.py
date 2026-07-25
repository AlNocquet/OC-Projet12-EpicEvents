"""
JWT authentication and local token storage.

This module creates, stores, loads and validates authentication tokens.
The current user is always reloaded from the database after token
validation.
"""

import json
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from src.core.config import (
    JWT_ALGORITHM,
    JWT_EXPIRATION_MINUTES,
    TOKEN_FILE_PATH,
    get_jwt_secret_key,
)
from src.models.user import User


def create_access_token(
    user: User,
) -> str:
    """Create a signed JWT for an authenticated collaborator."""

    issued_at = datetime.now(timezone.utc)
    expires_at = issued_at + timedelta(
        minutes=JWT_EXPIRATION_MINUTES,
    )

    payload = {
        "sub": str(user.id),
        "email": user.email,
        "department": user.department,
        "iat": issued_at,
        "exp": expires_at,
    }

    return jwt.encode(
        payload=payload,
        key=get_jwt_secret_key(),
        algorithm=JWT_ALGORITHM,
    )


def save_token(
    token: str,
) -> None:
    """Store the JWT in the local JSON session file."""

    token_data = {
        "access_token": token,
        "token_type": "Bearer",
    }

    TOKEN_FILE_PATH.write_text(
        json.dumps(
            token_data,
            indent=4,
        ),
        encoding="utf-8",
    )


def load_token() -> str:
    """Load the JWT stored in the local JSON session file."""

    if not TOKEN_FILE_PATH.exists():
        raise ValueError(
            "No authentication token found. Please log in."
        )

    try:
        token_data = json.loads(
            TOKEN_FILE_PATH.read_text(
                encoding="utf-8",
            )
        )

    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(
            "Authentication token file is invalid. Please log in again."
        ) from error

    token = token_data.get(
        "access_token",
    )

    if not isinstance(token, str) or not token.strip():
        raise ValueError(
            "Authentication token file is invalid. Please log in again."
        )

    return token


def decode_access_token(
    token: str,
) -> dict[str, Any]:
    """Validate a JWT and return its payload."""

    try:
        return jwt.decode(
            jwt=token,
            key=get_jwt_secret_key(),
            algorithms=[JWT_ALGORITHM],
            options={
                "require": [
                    "sub",
                    "iat",
                    "exp",
                ],
            },
        )

    except ExpiredSignatureError as error:
        raise ValueError(
            "Authentication token has expired. Please log in again."
        ) from error

    except InvalidTokenError as error:
        raise ValueError(
            "Authentication token is invalid. Please log in again."
        ) from error


def get_current_user_from_token() -> User:
    """
    Return the active database user identified by the stored JWT.

    The user and their current department are reloaded from SQLite
    instead of trusting authorization information stored in the token.
    """

    token = load_token()
    payload = decode_access_token(
        token=token,
    )

    subject = payload.get(
        "sub",
    )

    try:
        user_id = int(subject)

    except (TypeError, ValueError) as error:
        raise ValueError(
            "Authentication token is invalid. Please log in again."
        ) from error

    user = User.get_or_none(
        User.id == user_id,
    )

    if user is None:
        raise ValueError(
            "Authenticated user no longer exists."
        )

    if not user.is_active:
        raise ValueError(
            "Authenticated user account is inactive."
        )

    return user


def delete_token() -> bool:
    """Delete the locally stored JWT if it exists."""

    if not TOKEN_FILE_PATH.exists():
        return False

    TOKEN_FILE_PATH.unlink()
    return True