"""
Integration tests for JWT authentication and local session storage.
"""

import pytest

from src.core import jwt_auth

from src.core.jwt_auth import (
    create_access_token,
    decode_access_token,
    delete_token,
    get_current_user_from_token,
    load_token,
    save_token,
)


@pytest.fixture(autouse=True)
def isolate_jwt_configuration(
    tmp_path,
    monkeypatch,
):
    """Use an isolated secret and token file for every JWT test."""

    monkeypatch.setenv(
        "JWT_SECRET_KEY",
        "test-jwt-secret-key-for-hs256-integration-tests-2026",
    )

    monkeypatch.setattr(
        "src.core.jwt_auth.TOKEN_FILE_PATH",
        tmp_path / ".epic_events_token.json",
    )


def test_jwt_complete_session_flow(
    management_user,
):
    """A JWT session identifies the persisted active collaborator."""

    token = create_access_token(
        user=management_user,
    )

    payload = decode_access_token(
        token=token,
    )

    save_token(
        token=token,
    )

    stored_token = load_token()
    current_user = get_current_user_from_token()

    assert payload["sub"] == str(management_user.id)
    assert stored_token == token
    assert current_user.id == management_user.id
    assert current_user.email == management_user.email
    assert delete_token() is True


def test_load_token_rejects_missing_session():
    """Loading a missing local session requires a new login."""

    with pytest.raises(
        ValueError,
        match="No authentication token found. Please log in.",
    ):
        load_token()


def test_decode_access_token_rejects_invalid_token():
    """An invalid JWT requires a new login."""

    with pytest.raises(
        ValueError,
        match="Authentication token is invalid",
    ):
        decode_access_token(
            token="not-a-valid-jwt",
        )


def test_decode_access_token_rejects_expired_token(
    management_user,
    monkeypatch,
):
    """An expired JWT requires a new login."""

    monkeypatch.setattr(
        "src.core.jwt_auth.JWT_EXPIRATION_MINUTES",
        -1,
    )

    token = create_access_token(
        user=management_user,
    )

    with pytest.raises(
        ValueError,
        match="Authentication token has expired",
    ):
        decode_access_token(
            token=token,
        )


def test_get_current_user_rejects_inactive_account(
    management_user,
):
    """A valid JWT cannot authenticate a collaborator deactivated later."""

    token = create_access_token(
        user=management_user,
    )

    save_token(
        token=token,
    )

    management_user.is_active = False
    management_user.save()

    with pytest.raises(
        ValueError,
        match="Authenticated user account is inactive.",
    ):
        get_current_user_from_token()


def test_get_current_user_rejects_deleted_account(
    management_user,
):
    """A valid JWT cannot authenticate a deleted collaborator."""

    token = create_access_token(
        user=management_user,
    )

    save_token(
        token=token,
    )

    management_user.delete_instance()

    with pytest.raises(
        ValueError,
        match="Authenticated user no longer exists.",
    ):
        get_current_user_from_token()


def test_load_token_rejects_invalid_json_file():
    """A corrupted local session file requires a new login."""

    jwt_auth.TOKEN_FILE_PATH.write_text(
        "{invalid-json",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Authentication token file is invalid",
    ):
        load_token()


def test_delete_token_returns_false_when_session_is_missing():
    """Deleting an absent local session reports that nothing was removed."""

    assert delete_token() is False


def test_load_token_rejects_missing_access_token():
    """A session file without an access token requires a new login."""

    jwt_auth.TOKEN_FILE_PATH.write_text(
        '{"unexpected_key": "unexpected_value"}',
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Authentication token file is invalid",
    ):
        load_token()