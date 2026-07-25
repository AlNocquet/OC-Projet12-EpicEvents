"""
Application configuration.

This module centralizes database, monitoring and JWT configuration.
Sensitive values are read from environment variables.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")

DATABASE_PATH = BASE_DIR / "epic_events.db"

TOKEN_FILE_PATH = BASE_DIR / ".epic_events_token.json"

JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 100


def get_jwt_secret_key() -> str:
    """Return the secret key used to sign and validate JWT tokens."""

    secret_key = os.getenv("JWT_SECRET_KEY", "").strip()

    if not secret_key:
        raise ValueError(
            "JWT_SECRET_KEY environment variable is required."
        )

    return secret_key


def get_sentry_dsn() -> str:
    """Return the Sentry DSN configured in the environment."""

    return os.getenv("SENTRY_DSN", "").strip()


def get_sentry_environment() -> str:
    """Return the Sentry environment name."""

    return (
        os.getenv(
            "SENTRY_ENVIRONMENT",
            "development",
        ).strip()
        or "development"
    )