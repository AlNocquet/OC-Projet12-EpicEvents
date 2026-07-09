"""
user_service.py

Role:
- Implement user business logic.
- Validate business rules.
- Securely hash user passwords.
- Interact with the User model.

Database operations related to users are centralized in this module.
"""

from passlib.hash import bcrypt

from src.models.user import User


VALID_DEPARTMENTS = {
    "COMMERCIAL",
    "SUPPORT",
    "MANAGEMENT",
}


def create_user(
    full_name: str,
    email: str,
    password: str,
    department: str,
) -> User:
    """
    Create a new user account.

    Validates the provided user information, securely hashes the
    password and stores the new user in the database.

    Raises:
        ValueError: If the provided data is invalid or the email
        address is already registered.
    """

    full_name = full_name.strip()
    email = email.strip()
    password = password.strip()
    department = department.strip().upper()

    if not full_name:
        raise ValueError("Full name is required.")

    if not email:
        raise ValueError("Email is required.")

    if not password:
        raise ValueError("Password is required.")

    if department not in VALID_DEPARTMENTS:
        raise ValueError("Invalid department.")

    existing_user = User.get_or_none(
        User.email == email
    )

    if existing_user:
        raise ValueError(
            "A user with this email already exists."
        )

    password_hash = bcrypt.hash(password)

    return User.create(
        full_name=full_name,
        email=email,
        password_hash=password_hash,
        department=department,
    )