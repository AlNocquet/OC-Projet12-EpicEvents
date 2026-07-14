"""
client_service.py

Role:
- Implement client business logic.
- Validate client data.
- Enforce client management permissions.
- Interact with the Client model.

All client-related database operations are centralized in this module.
"""

from datetime import datetime

from src.auth import require_permission

from src.models.client import Client
from src.models.user import User


CLIENT_READ_DEPARTMENTS = (
    "COMMERCIAL",
    "SUPPORT",
    "MANAGEMENT",
)


def _validate_client_data(
    full_name: str,
    email: str,
    phone: str,
    company_name: str,
) -> tuple[str, str, str, str]:
    """
    Normalize and validate required client information.

    Returns:
        The normalized full name, email, phone number and company name.

    Raises:
        ValueError: If one of the required fields is empty.
    """

    full_name = full_name.strip()
    email = email.strip().lower()
    phone = phone.strip()
    company_name = company_name.strip()

    if not full_name:
        raise ValueError("Full name is required.")

    if not email:
        raise ValueError("Email is required.")

    if not phone:
        raise ValueError("Phone number is required.")

    if not company_name:
        raise ValueError("Company name is required.")

    return full_name, email, phone, company_name


def _get_client_by_id(
    client_id: int,
) -> Client:
    """
    Retrieve a client by identifier.

    Raises:
        ValueError: If no client matches the provided identifier.
    """

    client = Client.get_or_none(
        Client.id == client_id
    )

    if client is None:
        raise ValueError("Client not found.")

    return client


def create_client(
    full_name: str,
    email: str,
    phone: str,
    company_name: str,
    current_user: User,
) -> Client:
    """
    Create a new client.

    Only an authenticated and active commercial user may create a
    client. The commercial is automatically assigned as the client's
    sales contact.

    Raises:
        PermissionError: If the current user is not authorized.
        ValueError: If the provided data is invalid or the email
        address is already registered.
    """

    require_permission(
        current_user,
        "COMMERCIAL",
    )

    full_name, email, phone, company_name = _validate_client_data(
        full_name=full_name,
        email=email,
        phone=phone,
        company_name=company_name,
    )

    existing_client = Client.get_or_none(
        Client.email == email
    )

    if existing_client:
        raise ValueError(
            "A client with this email already exists."
        )

    return Client.create(
        full_name=full_name,
        email=email,
        phone=phone,
        company_name=company_name,
        sales_contact=current_user,
    )


def list_all_clients(
    current_user: User,
) -> list[Client]:
    """
    Retrieve every client stored in the CRM.

    All authenticated and active collaborators may access client
    information in read-only mode.

    Returns:
        A list of clients ordered by company name and full name.

    Raises:
        PermissionError: If the current user is not authorized.
    """

    require_permission(
        current_user,
        *CLIENT_READ_DEPARTMENTS,
    )

    return list(
        Client.select().order_by(
            Client.company_name,
            Client.full_name,
        )
    )


def update_client(
    client_id: int,
    full_name: str,
    email: str,
    phone: str,
    company_name: str,
    current_user: User,
) -> Client:
    """
    Update an existing client.

    Only an authenticated and active commercial user may update a
    client, and only when that commercial is the client's assigned
    sales contact.

    Raises:
        PermissionError: If the current user is not authorized.
        ValueError: If the client does not exist, the provided data is
        invalid or the email belongs to another client.
    """

    require_permission(
        current_user,
        "COMMERCIAL",
    )

    client = _get_client_by_id(
        client_id=client_id,
    )

    if client.sales_contact_id != current_user.id:
        raise PermissionError(
            "You can only update your own clients."
        )

    full_name, email, phone, company_name = _validate_client_data(
        full_name=full_name,
        email=email,
        phone=phone,
        company_name=company_name,
    )

    existing_client = Client.get_or_none(
        (Client.email == email)
        & (Client.id != client.id)
    )

    if existing_client:
        raise ValueError(
            "A client with this email already exists."
        )

    client.full_name = full_name
    client.email = email
    client.phone = phone
    client.company_name = company_name
    client.updated_at = datetime.now()

    client.save()

    return client