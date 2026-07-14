"""
test_auth.py

Tests for the authentication and authorization module.
"""

import pytest

from src.auth import (
    authenticate_user,
    check_user_department,
    has_required_permission,
    require_permission,
)


def test_authenticate_user_success(
    management_user,
):
    """
    Happy Path

    An active user is authenticated with valid credentials.
    """

    user = authenticate_user(
        email="manager@epicevents.com",
        password="ManagementPassword123!",
    )

    assert user is not None
    assert user.id == management_user.id
    assert user.full_name == "Morgan Manager"


def test_authenticate_user_normalizes_email(
    management_user,
):
    """
    Happy Path

    Authentication normalizes spaces and uppercase letters in
    the email address.
    """

    user = authenticate_user(
        email="  MANAGER@EPICEVENTS.COM  ",
        password="ManagementPassword123!",
    )

    assert user is not None
    assert user.id == management_user.id


def test_authenticate_user_with_unknown_email(
    test_database,
):
    """
    Sad Path

    Authentication fails when the email does not exist.
    """

    user = authenticate_user(
        email="unknown@epicevents.com",
        password="SecurePassword123!",
    )

    assert user is None


def test_authenticate_user_with_wrong_password(
    management_user,
):
    """
    Sad Path

    Authentication fails when the password is incorrect.
    """

    user = authenticate_user(
        email="manager@epicevents.com",
        password="WrongPassword123!",
    )

    assert user is None


def test_authenticate_user_with_inactive_account(
    commercial_user,
):
    """
    Sad Path

    An inactive collaborator cannot authenticate.
    """

    commercial_user.is_active = False
    commercial_user.save()

    user = authenticate_user(
        email="commercial@epicevents.com",
        password="CommercialPassword123!",
    )

    assert user is None


def test_authenticate_user_with_empty_email(
    test_database,
):
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


def test_authenticate_user_with_empty_password(
    test_database,
):
    """
    Sad Path

    Authentication fails when the password is empty.
    """

    with pytest.raises(
        ValueError,
        match="Password is required.",
    ):
        authenticate_user(
            email="manager@epicevents.com",
            password="",
        )


def test_check_user_department_success(
    management_user,
):
    """
    Happy Path

    The collaborator belongs to the expected department.
    """

    assert check_user_department(
        management_user,
        "management",
    )


def test_check_user_department_failure(
    commercial_user,
):
    """
    Sad Path

    The collaborator does not belong to the expected department.
    """

    assert not check_user_department(
        commercial_user,
        "SUPPORT",
    )


def test_has_required_permission_success(
    management_user,
):
    """
    Happy Path

    A management collaborator has the required permission.
    """

    assert has_required_permission(
        management_user,
        "MANAGEMENT",
    )


def test_has_required_permission_with_multiple_departments(
    support_user,
):
    """
    Happy Path

    A collaborator is authorized when their department appears
    among several authorized departments.
    """

    assert has_required_permission(
        support_user,
        "COMMERCIAL",
        "SUPPORT",
        "MANAGEMENT",
    )


def test_has_required_permission_failure(
    commercial_user,
):
    """
    Sad Path

    A collaborator without the required permission is rejected.
    """

    assert not has_required_permission(
        commercial_user,
        "MANAGEMENT",
    )


def test_inactive_user_has_no_permission(
    management_user,
):
    """
    Sad Path

    An inactive collaborator has no permission.
    """

    management_user.is_active = False
    management_user.save()

    assert not has_required_permission(
        management_user,
        "MANAGEMENT",
    )


def test_require_permission_success(
    management_user,
):
    """
    Happy Path

    No exception is raised when the collaborator is authorized.
    """

    require_permission(
        management_user,
        "MANAGEMENT",
    )


def test_require_permission_failure(
    support_user,
):
    """
    Sad Path

    An unauthorized collaborator triggers a PermissionError.
    """

    with pytest.raises(
        PermissionError,
        match="Permission denied.",
    ):
        require_permission(
            support_user,
            "MANAGEMENT",
        )


def test_require_permission_rejects_inactive_user(
    management_user,
):
    """
    Sad Path

    An inactive collaborator triggers a PermissionError.
    """

    management_user.is_active = False
    management_user.save()

    with pytest.raises(
        PermissionError,
        match="Permission denied.",
    ):
        require_permission(
            management_user,
            "MANAGEMENT",
        )