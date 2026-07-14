"""
user_service.py

Role:
- Implement collaborator business logic.
- Validate collaborator data.
- Securely hash passwords.
- Enforce management permissions.
- Interact with the User model.

All collaborator-related database operations are centralized in this module.
"""

from typing import Optional

from passlib.hash import bcrypt

from src.auth import require_permission
from src.models.user import User


VALID_DEPARTMENTS = {
    "COMMERCIAL",
    "SUPPORT",
    "MANAGEMENT",
}


def _validate_user_profile(
    full_name: str,
    email: str,
    department: str,
) -> tuple[str, str, str]:
    """
    Normalize and validate collaborator profile information.

    Returns:
        The normalized full name, email address and department.

    Raises:
        ValueError: If required data is missing or the department is
        invalid.
    """

    full_name = full_name.strip()
    email = email.strip().lower()
    department = department.strip().upper()

    if not full_name:
        raise ValueError("Full name is required.")

    if not email:
        raise ValueError("Email is required.")

    if department not in VALID_DEPARTMENTS:
        raise ValueError("Invalid department.")

    return full_name, email, department


def _validate_password(
    password: str,
) -> str:
    """
    Validate a password before hashing.

    Raises:
        ValueError: If the password is empty.
    """

    if not password or not password.strip():
        raise ValueError("Password is required.")

    return password


def _get_user_by_id(
    user_id: int,
) -> User:
    """
    Retrieve a collaborator by identifier.

    Raises:
        ValueError: If no collaborator matches the identifier.
    """

    user = User.get_or_none(
        User.id == user_id
    )

    if user is None:
        raise ValueError("User not found.")

    return user


def _ensure_email_is_available(
    email: str,
    excluded_user_id: Optional[int] = None,
) -> None:
    """
    Ensure that an email address is not assigned to another user.

    Raises:
        ValueError: If the email address is already registered.
    """

    query = User.email == email

    if excluded_user_id is not None:
        query &= User.id != excluded_user_id

    existing_user = User.get_or_none(query)

    if existing_user:
        raise ValueError(
            "A user with this email already exists."
        )


def _create_user_record(
    full_name: str,
    email: str,
    password: str,
    department: str,
) -> User:
    """
    Create a validated collaborator record in the database.
    """

    _ensure_email_is_available(
        email=email,
    )

    return User.create(
        full_name=full_name,
        email=email,
        password_hash=bcrypt.hash(password),
        department=department,
    )


def create_initial_management_user(
    full_name: str,
    email: str,
    password: str,
) -> User:
    """
    Create the first management account.

    This operation is only permitted while the database contains no
    collaborator.

    Raises:
        PermissionError: If a collaborator already exists.
        ValueError: If the provided data is invalid.
    """

    if User.select().exists():
        raise PermissionError(
            "Initial management account already exists."
        )

    full_name, email, department = _validate_user_profile(
        full_name=full_name,
        email=email,
        department="MANAGEMENT",
    )

    password = _validate_password(
        password=password,
    )

    return _create_user_record(
        full_name=full_name,
        email=email,
        password=password,
        department=department,
    )


def create_user(
    full_name: str,
    email: str,
    password: str,
    department: str,
    current_user: User,
) -> User:
    """
    Create a new collaborator account.

    Only an authenticated and active management user may create a
    collaborator.

    Raises:
        PermissionError: If the current user is not authorized.
        ValueError: If the provided data is invalid or the email
        address is already registered.
    """

    require_permission(
        current_user,
        "MANAGEMENT",
    )

    full_name, email, department = _validate_user_profile(
        full_name=full_name,
        email=email,
        department=department,
    )

    password = _validate_password(
        password=password,
    )

    return _create_user_record(
        full_name=full_name,
        email=email,
        password=password,
        department=department,
    )


def update_user(
    user_id: int,
    full_name: str,
    email: str,
    department: str,
    current_user: User,
) -> User:
    """
    Update an existing collaborator account.

    Only an authenticated and active management user may update a
    collaborator.

    Raises:
        PermissionError: If the current user is not authorized or
        attempts to remove their own management role.
        ValueError: If the collaborator does not exist, the provided
        data is invalid or the email belongs to another collaborator.
    """

    require_permission(
        current_user,
        "MANAGEMENT",
    )

    user = _get_user_by_id(
        user_id=user_id,
    )

    full_name, email, department = _validate_user_profile(
        full_name=full_name,
        email=email,
        department=department,
    )

    if (
        user.id == current_user.id
        and department != "MANAGEMENT"
    ):
        raise PermissionError(
            "You cannot change your own management department."
        )

    _ensure_email_is_available(
        email=email,
        excluded_user_id=user.id,
    )

    user.full_name = full_name
    user.email = email
    user.department = department

    user.save(
        only=[
            User.full_name,
            User.email,
            User.department,
        ]
    )

    return user


def delete_user(
    user_id: int,
    current_user: User,
) -> User:
    """
    Delete a collaborator account by deactivating it.

    Deactivation preserves CRM records linked to the collaborator while
    preventing further authentication.

    Raises:
        PermissionError: If the current user is not authorized or
        attempts to delete their own account.
        ValueError: If the collaborator does not exist or is already
        inactive.
    """

    require_permission(
        current_user,
        "MANAGEMENT",
    )

    user = _get_user_by_id(
        user_id=user_id,
    )

    if user.id == current_user.id:
        raise PermissionError(
            "You cannot delete your own account."
        )

    if not user.is_active:
        raise ValueError(
            "User is already inactive."
        )

    user.is_active = False

    user.save(
        only=[
            User.is_active,
        ]
    )

    return user