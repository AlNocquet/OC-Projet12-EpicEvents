"""
config.py

Role:
- Store application configuration.
- Centralize configurable values.
- Read monitoring configuration from environment variables.
"""

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "epic_events.db"


def get_sentry_dsn() -> str:
    """Return the Sentry DSN configured in the environment."""

    return os.getenv(
        "SENTRY_DSN",
        "",
    ).strip()


def get_sentry_environment() -> str:
    """Return the Sentry environment name."""

    return (
        os.getenv(
            "SENTRY_ENVIRONMENT",
            "development",
        ).strip()
        or "development"
    )
