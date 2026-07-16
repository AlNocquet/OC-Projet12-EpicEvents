"""
monitoring.py

Role:
- Initialize Sentry error monitoring.
- Capture unexpected application exceptions.
- Provide a controlled Sentry demonstration event.
- Keep monitoring secrets outside the source code.
"""

from typing import Optional

import sentry_sdk

from src.config import (
    get_sentry_dsn,
    get_sentry_environment,
)


def initialize_sentry() -> bool:
    """Initialize Sentry when a DSN is available."""

    dsn = get_sentry_dsn()

    if not dsn:
        return False

    sentry_sdk.init(
        dsn=dsn,
        environment=get_sentry_environment(),
        send_default_pii=False,
        include_local_variables=False,
        traces_sample_rate=None,
        enable_logs=True,
    )

    return True


def capture_application_exception(
    error: BaseException,
) -> Optional[str]:
    """Send an exception to Sentry and flush the transport queue."""

    event_id = sentry_sdk.capture_exception(
        error,
    )

    sentry_sdk.flush(
        timeout=2.0,
    )

    if event_id is None:
        return None

    return str(event_id)


def send_test_exception() -> Optional[str]:
    """Generate and capture a controlled exception for demonstration."""

    try:
        raise RuntimeError(
            "Epic Events controlled Sentry demonstration error."
        )

    except RuntimeError as error:
        return capture_application_exception(
            error=error,
        )
