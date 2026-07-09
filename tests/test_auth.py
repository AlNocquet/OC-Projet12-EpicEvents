"""
test_auth.py

Tests for the authentication and authorization module.
"""

import pytest

from src.auth import (
    authenticate_user,
    has_required_permission,
    require_permission,
)
from src.user_service import create_user


def test_authenticate_user_success(test_database):
    """
    Happy Path

    A user is successfully authenticated with valid credentials.
    """

    create_user(
        full_name="John Doe",
        email="john.doe@email.com",
        password="SecurePassword123!",
        department="MANAGEMENT",
    )

    user = authenticate_user(
        email="john.doe@email.com",
        password="SecurePassword123!",
    )

    assert user is not None
    assert user.full_name == "John Doe"


def test_authenticate_user_with_unknown_email(test_database):
    """
    Sad Path

    Authentication fails when the email does not exist.
    """

    user = authenticate_user(
        email="unknown@email.com",
        password="SecurePassword123!",
    )

    assert user is None


def test_authenticate_user_with_wrong_password(test_database):
    """
    Sad Path

    Authentication fails when the password is incorrect.
    """

    create_user(
        full_name="John Doe",
        email="john.doe@email.com",
        password="SecurePassword123!",
        department="MANAGEMENT",
    )

    user = authenticate_user(
        email="john.doe@email.com",
        password="WrongPassword123!",
    )

    assert user is None


def test_authenticate_user_with_empty_email(test_database):
    """
    Sad Path

    Authentication fails when the email is empty.
    """

    with pytest.raises(
        ValueError,
        match="Email is required.",
    ):
        authenticate_user(
            email="",
            password="SecurePassword123!",
        )


def test_authenticate_user_with_empty_password(test_database):
    """
    Sad Path

    Authentication fails when the password is empty.
    """

    with pytest.raises(
        ValueError,
        match="Password is required.",
    ):
        authenticate_user(
            email="john.doe@email.com",
            password="",
        )


def test_has_required_permission_success(test_database):
    """
    Happy Path

    A management user has the required permission.
    """

    user = create_user(
        full_name="John Doe",
        email="john.doe@email.com",
        password="SecurePassword123!",
        department="MANAGEMENT",
    )

    assert has_required_permission(
        user,
        "MANAGEMENT",
    )


def test_has_required_permission_failure(test_database):
    """
    Sad Path

    A user without the required permission is rejected.
    """

    user = create_user(
        full_name="John Doe",
        email="john.doe@email.com",
        password="SecurePassword123!",
        department="COMMERCIAL",
    )

    assert not has_required_permission(
        user,
        "MANAGEMENT",
    )


def test_require_permission_success(test_database):
    """
    Happy Path

    No exception is raised when the user has the required permission.
    """

    user = create_user(
        full_name="John Doe",
        email="john.doe@email.com",
        password="SecurePassword123!",
        department="MANAGEMENT",
    )

    require_permission(
        user,
        "MANAGEMENT",
    )


def test_require_permission_failure(test_database):
    """
    Sad Path

    A PermissionError is raised when the user does not have the required permission.
    """

    user = create_user(
        full_name="John Doe",
        email="john.doe@email.com",
        password="SecurePassword123!",
        department="SUPPORT",
    )

    with pytest.raises(
        PermissionError,
        match="Permission denied.",
    ):
        require_permission(
            user,
            "MANAGEMENT",
        )