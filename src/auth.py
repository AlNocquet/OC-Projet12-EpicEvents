"""
auth.py

Role:
- Authenticate application users.
- Verify user credentials.
- Enforce role-based authorization.
- Protect access to restricted application features.

This module centralizes every authentication and authorization rule.
"""

from typing import Optional

from passlib.hash import bcrypt
from peewee import DoesNotExist

from src.models.user import User


def authenticate_user(
    email: str,
    password: str,
) -> Optional[User]:
    """
    Authenticate an active user using an email address and a password.

    Returns the authenticated user when the credentials are valid and
    the account is active. Otherwise, returns None.

    Raises:
        ValueError: If the email or password is empty.
    """

    email = email.strip().lower()

    if not email:
        raise ValueError("Email is required.")

    if not password or not password.strip():
        raise ValueError("Password is required.")

    try:
        user = User.get(User.email == email)

    except DoesNotExist:
        return None

    if not user.is_active:
        return None

    if bcrypt.verify(password, user.password_hash):
        return user

    return None


def check_user_department(
    user: Optional[User],
    department: str,
) -> bool:
    """
    Verify whether an active user belongs to the specified department.
    """

    if user is None or not user.is_active:
        return False

    return user.department == department.strip().upper()


def has_required_permission(
    user: Optional[User],
    *authorized_departments: str,
) -> bool:
    """
    Verify whether an active user belongs to one of the authorized
    departments.
    """

    if user is None or not user.is_active:
        return False

    normalized_departments = tuple(
        department.strip().upper()
        for department in authorized_departments
    )

    return user.department in normalized_departments


def require_permission(
    user: Optional[User],
    *authorized_departments: str,
) -> None:
    """
    Enforce role-based authorization.

    Raises:
        PermissionError: If the user is inactive, unauthenticated or
        does not belong to an authorized department.
    """

    if not has_required_permission(
        user,
        *authorized_departments,
    ):
        raise PermissionError("Permission denied.")