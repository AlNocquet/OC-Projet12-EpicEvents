"""
test_user_service.py

Tests for the user service layer.
"""

import pytest

from src.models.user import User
from src.user_service import create_user


def test_create_user_success(test_database):
    """
    Happy Path

    A user is successfully created with valid information.
    """

    user = create_user(
        full_name="John Doe",
        email="john.doe@email.com",
        password="SecurePassword123!",
        department="MANAGEMENT",
    )

    assert user.full_name == "John Doe"
    assert user.email == "john.doe@email.com"
    assert user.department == "MANAGEMENT"
    assert user.password_hash != "SecurePassword123!"
    assert User.select().count() == 1


def test_create_user_with_empty_full_name(test_database):
    """
    Sad Path

    Creating a user without a full name raises an error.
    """

    with pytest.raises(
        ValueError,
        match="Full name is required.",
    ):
        create_user(
            full_name="",
            email="john.doe@email.com",
            password="SecurePassword123!",
            department="MANAGEMENT",
        )


def test_create_user_with_empty_email(test_database):
    """
    Sad Path

    Creating a user without an email raises an error.
    """

    with pytest.raises(
        ValueError,
        match="Email is required.",
    ):
        create_user(
            full_name="John Doe",
            email="",
            password="SecurePassword123!",
            department="MANAGEMENT",
        )


def test_create_user_with_empty_password(test_database):
    """
    Sad Path

    Creating a user without a password raises an error.
    """

    with pytest.raises(
        ValueError,
        match="Password is required.",
    ):
        create_user(
            full_name="John Doe",
            email="john.doe@email.com",
            password="",
            department="MANAGEMENT",
        )


def test_create_user_with_invalid_department(test_database):
    """
    Sad Path

    Creating a user with an invalid department raises an error.
    """

    with pytest.raises(
        ValueError,
        match="Invalid department.",
    ):
        create_user(
            full_name="John Doe",
            email="john.doe@email.com",
            password="SecurePassword123!",
            department="CEO",
        )


def test_create_user_with_existing_email(test_database):
    """
    Sad Path

    Creating two users with the same email raises an error.
    """

    create_user(
        full_name="John Doe",
        email="john.doe@email.com",
        password="SecurePassword123!",
        department="MANAGEMENT",
    )

    with pytest.raises(
        ValueError,
        match="A user with this email already exists.",
    ):
        create_user(
            full_name="Jane Doe",
            email="john.doe@email.com",
            password="AnotherPassword123!",
            department="SUPPORT",
        )