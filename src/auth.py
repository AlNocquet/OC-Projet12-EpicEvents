"""
auth.py

Role:
- Authenticate application users.
- Verify user credentials.
- Enforce role-based authorization.
- Protect access to restricted application features.

This module centralizes every authentication and authorization rule.
"""

from peewee import DoesNotExist
from passlib.hash import bcrypt

from src.models.user import User


def authenticate_user(
    email: str,
    password: str,
) -> User | None:
    """
    Authenticate a user using an email address and a password.

    The provided password is verified against the securely stored
    password hash. Returns the authenticated user when the
    credentials are valid, otherwise returns None.
    """

    email = email.strip()
    password = password.strip()

    if not email:
        raise ValueError("Email is required.")

    if not password:
        raise ValueError("Password is required.")

    try:
        user = User.get(User.email == email)

    except DoesNotExist:
        return None

    if bcrypt.verify(password, user.password_hash):
        return user

    return None


def check_user_department(
    user: User,
    department: str,
) -> bool:
    """
    Verify whether a user belongs to the specified department.

    Returns True when the user's department matches the expected
    department, otherwise returns False.
    """

    return user.department == department.strip().upper()


def has_required_permission(
    user: User,
    *authorized_departments: str,
) -> bool:
    """
    Verify whether a user belongs to one of the authorized
    departments.

    Returns True when the user is authorized, otherwise returns
    False.
    """

    authorized_departments = tuple(
        department.strip().upper()
        for department in authorized_departments
    )

    return user.department in authorized_departments


def require_permission(
    user: User,
    *authorized_departments: str,
) -> None:
    """
    Enforce role-based authorization.

    Raises a PermissionError when the authenticated user does not
    belong to one of the authorized departments.
    """

    if not has_required_permission(
        user,
        *authorized_departments,
    ):
        raise PermissionError("Permission denied.")