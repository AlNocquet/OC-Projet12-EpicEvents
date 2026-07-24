"""
Tests for Sentry monitoring configuration and exception capture.
"""

from unittest.mock import Mock

from src.core.monitoring import (
    capture_application_exception,
    initialize_sentry,
    send_test_exception,
)


def test_initialize_sentry_without_dsn(
    monkeypatch,
):
    """Sentry remains disabled when no DSN is configured."""

    monkeypatch.delenv(
        "SENTRY_DSN",
        raising=False,
    )

    sentry_init = Mock()
    monkeypatch.setattr(
        "src.core.monitoring.sentry_sdk.init",
        sentry_init,
    )

    assert initialize_sentry() is False
    sentry_init.assert_not_called()


def test_initialize_sentry_with_environment_configuration(
    monkeypatch,
):
    """Sentry reads its secure configuration from the environment."""

    monkeypatch.setenv(
        "SENTRY_DSN",
        "https://public@example.ingest.sentry.io/123",
    )
    monkeypatch.setenv(
        "SENTRY_ENVIRONMENT",
        "test",
    )

    sentry_init = Mock()
    monkeypatch.setattr(
        "src.core.monitoring.sentry_sdk.init",
        sentry_init,
    )

    assert initialize_sentry() is True

    sentry_init.assert_called_once_with(
        dsn="https://public@example.ingest.sentry.io/123",
        environment="test",
        send_default_pii=False,
        include_local_variables=False,
        traces_sample_rate=None,
        enable_logs=True,
    )


def test_capture_application_exception(
    monkeypatch,
):
    """Captured exceptions are flushed and return an event ID."""

    capture_exception = Mock(
        return_value="event-123",
    )
    flush = Mock()

    monkeypatch.setattr(
        "src.core.monitoring.sentry_sdk.capture_exception",
        capture_exception,
    )
    monkeypatch.setattr(
        "src.core.monitoring.sentry_sdk.flush",
        flush,
    )

    error = RuntimeError(
        "Unexpected failure."
    )

    event_id = capture_application_exception(
        error=error,
    )

    assert event_id == "event-123"
    capture_exception.assert_called_once_with(
        error,
    )
    flush.assert_called_once_with(
        timeout=2.0,
    )


def test_send_test_exception(
    monkeypatch,
):
    """The demonstration helper sends a controlled RuntimeError."""

    captured_errors = []

    def fake_capture(
        error,
    ):
        captured_errors.append(
            error,
        )
        return "demo-event"

    monkeypatch.setattr(
        "src.core.monitoring.capture_application_exception",
        fake_capture,
    )

    event_id = send_test_exception()

    assert event_id == "demo-event"
    assert len(captured_errors) == 1
    assert isinstance(
        captured_errors[0],
        RuntimeError,
    )
