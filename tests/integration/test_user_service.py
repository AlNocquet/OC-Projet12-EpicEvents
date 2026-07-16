"""
test_user_service.py

Tests for the collaborator service layer.
"""

import pytest
from passlib.hash import bcrypt

from src.models.user import User

from src.services.user_service import (
    create_initial_management_user,
    create_user,
    delete_user,
    update_user,
)


def test_create_initial_management_user_success(
    test_database,
):
    """
    Happy Path

    The first management collaborator is created successfully.
    """

    user = create_initial_management_user(
        full_name="Morgan Manager",
        email="MANAGER@EPICEVENTS.COM",
        password="ManagementPassword123!",
    )

    assert user.full_name == "Morgan Manager"
    assert user.email == "manager@epicevents.com"
    assert user.department == "MANAGEMENT"
    assert user.is_active is True
    assert bcrypt.verify(
        "ManagementPassword123!",
        user.password_hash,
    )
    assert User.select().count() == 1


def test_create_second_initial_management_user_is_rejected(
    management_user,
):
    """
    Sad Path

    The initial management command cannot create another account
    after the first collaborator exists.
    """

    with pytest.raises(
        PermissionError,
        match="Initial management account already exists.",
    ):
        create_initial_management_user(
            full_name="Another Manager",
            email="another.manager@epicevents.com",
            password="AnotherPassword123!",
        )


def test_create_user_success(
    management_user,
):
    """
    Happy Path

    A management collaborator creates another collaborator.
    """

    user = create_user(
        full_name="Casey Commercial",
        email="COMMERCIAL@EPICEVENTS.COM",
        password="CommercialPassword123!",
        department="commercial",
        current_user=management_user,
    )

    assert user.full_name == "Casey Commercial"
    assert user.email == "commercial@epicevents.com"
    assert user.department == "COMMERCIAL"
    assert user.is_active is True
    assert bcrypt.verify(
        "CommercialPassword123!",
        user.password_hash,
    )
    assert User.select().count() == 2


def test_create_user_without_management_permission(
    commercial_user,
):
    """
    Sad Path

    A commercial collaborator cannot create another collaborator.
    """

    with pytest.raises(
        PermissionError,
        match="Permission denied.",
    ):
        create_user(
            full_name="Sam Support",
            email="support@epicevents.com",
            password="SupportPassword123!",
            department="SUPPORT",
            current_user=commercial_user,
        )


def test_create_user_with_empty_full_name(
    management_user,
):
    """
    Sad Path

    Creating a collaborator without a full name raises an error.
    """

    with pytest.raises(
        ValueError,
        match="Full name is required.",
    ):
        create_user(
            full_name="",
            email="commercial@epicevents.com",
            password="CommercialPassword123!",
            department="COMMERCIAL",
            current_user=management_user,
        )


def test_create_user_with_empty_email(
    management_user,
):
    """
    Sad Path

    Creating a collaborator without an email raises an error.
    """

    with pytest.raises(
        ValueError,
        match="Email is required.",
    ):
        create_user(
            full_name="Casey Commercial",
            email="",
            password="CommercialPassword123!",
            department="COMMERCIAL",
            current_user=management_user,
        )


def test_create_user_with_empty_password(
    management_user,
):
    """
    Sad Path

    Creating a collaborator without a password raises an error.
    """

    with pytest.raises(
        ValueError,
        match="Password is required.",
    ):
        create_user(
            full_name="Casey Commercial",
            email="commercial@epicevents.com",
            password="",
            department="COMMERCIAL",
            current_user=management_user,
        )


def test_create_user_with_invalid_department(
    management_user,
):
    """
    Sad Path

    Creating a collaborator with an invalid department raises an error.
    """

    with pytest.raises(
        ValueError,
        match="Invalid department.",
    ):
        create_user(
            full_name="Casey Commercial",
            email="commercial@epicevents.com",
            password="CommercialPassword123!",
            department="CEO",
            current_user=management_user,
        )


def test_create_user_with_existing_email(
    management_user,
    commercial_user,
):
    """
    Sad Path

    Two collaborators cannot share the same email address.
    """

    with pytest.raises(
        ValueError,
        match="A user with this email already exists.",
    ):
        create_user(
            full_name="Another Commercial",
            email="COMMERCIAL@EPICEVENTS.COM",
            password="AnotherPassword123!",
            department="COMMERCIAL",
            current_user=management_user,
        )


def test_update_user_success(
    management_user,
    commercial_user,
):
    """
    Happy Path

    A management collaborator updates another collaborator.
    """

    updated_user = update_user(
        user_id=commercial_user.id,
        full_name="Casey Updated",
        email="UPDATED@EPICEVENTS.COM",
        department="support",
        current_user=management_user,
    )

    assert updated_user.id == commercial_user.id
    assert updated_user.full_name == "Casey Updated"
    assert updated_user.email == "updated@epicevents.com"
    assert updated_user.department == "SUPPORT"


def test_update_unknown_user(
    management_user,
):
    """
    Sad Path

    Updating an unknown collaborator raises an error.
    """

    with pytest.raises(
        ValueError,
        match="User not found.",
    ):
        update_user(
            user_id=9999,
            full_name="Unknown User",
            email="unknown@epicevents.com",
            department="SUPPORT",
            current_user=management_user,
        )


def test_update_user_without_management_permission(
    commercial_user,
    support_user,
):
    """
    Sad Path

    A commercial collaborator cannot update another collaborator.
    """

    with pytest.raises(
        PermissionError,
        match="Permission denied.",
    ):
        update_user(
            user_id=support_user.id,
            full_name="Updated Support",
            email="updated.support@epicevents.com",
            department="SUPPORT",
            current_user=commercial_user,
        )


def test_update_user_with_existing_email(
    management_user,
    commercial_user,
    support_user,
):
    """
    Sad Path

    Updating a collaborator with another collaborator's email
    raises an error.
    """

    with pytest.raises(
        ValueError,
        match="A user with this email already exists.",
    ):
        update_user(
            user_id=support_user.id,
            full_name=support_user.full_name,
            email=commercial_user.email,
            department=support_user.department,
            current_user=management_user,
        )


def test_management_user_cannot_remove_own_management_role(
    management_user,
):
    """
    Sad Path

    A management collaborator cannot remove their own management role.
    """

    with pytest.raises(
        PermissionError,
        match="You cannot change your own management department.",
    ):
        update_user(
            user_id=management_user.id,
            full_name=management_user.full_name,
            email=management_user.email,
            department="COMMERCIAL",
            current_user=management_user,
        )


def test_delete_user_success(
    management_user,
    commercial_user,
):
    """
    Happy Path

    Deleting a collaborator deactivates the account without removing
    the database record.
    """

    deleted_user = delete_user(
        user_id=commercial_user.id,
        current_user=management_user,
    )

    stored_user = User.get_by_id(
        commercial_user.id
    )

    assert deleted_user.is_active is False
    assert stored_user.is_active is False
    assert User.select().count() == 2


def test_delete_user_without_management_permission(
    commercial_user,
    support_user,
):
    """
    Sad Path

    A commercial collaborator cannot delete another collaborator.
    """

    with pytest.raises(
        PermissionError,
        match="Permission denied.",
    ):
        delete_user(
            user_id=support_user.id,
            current_user=commercial_user,
        )


def test_management_user_cannot_delete_own_account(
    management_user,
):
    """
    Sad Path

    A management collaborator cannot delete their own account.
    """

    with pytest.raises(
        PermissionError,
        match="You cannot delete your own account.",
    ):
        delete_user(
            user_id=management_user.id,
            current_user=management_user,
        )


def test_delete_already_inactive_user(
    management_user,
    commercial_user,
):
    """
    Sad Path

    Deleting an already inactive collaborator raises an error.
    """

    commercial_user.is_active = False
    commercial_user.save()

    with pytest.raises(
        ValueError,
        match="User is already inactive.",
    ):
        delete_user(
            user_id=commercial_user.id,
            current_user=management_user,
        )