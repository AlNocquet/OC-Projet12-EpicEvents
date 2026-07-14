"""
contract_service.py

Role:
- Implement contract business logic.
- Validate contract financial data.
- Enforce contract-management permissions.
- Interact with the Contract model.

All contract-related database operations are centralized in this module.
"""

from decimal import Decimal, InvalidOperation

from src.auth import (
    has_required_permission,
    require_permission,
)
from src.models.client import Client
from src.models.contract import Contract
from src.models.user import User


CONTRACT_READ_DEPARTMENTS = (
    "COMMERCIAL",
    "SUPPORT",
    "MANAGEMENT",
)


def _normalize_amount(
    value: Decimal | int | float | str,
    field_name: str,
) -> Decimal:
    """
    Convert a monetary value into a finite Decimal.

    Returns:
        The normalized monetary value.

    Raises:
        ValueError: If the provided value is not a valid finite number.
    """

    try:
        amount = Decimal(str(value))

    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(
            f"{field_name} must be a valid number."
        )

    if not amount.is_finite():
        raise ValueError(
            f"{field_name} must be a valid number."
        )

    return amount


def _validate_contract_amounts(
    total_amount: Decimal | int | float | str,
    amount_due: Decimal | int | float | str,
) -> tuple[Decimal, Decimal]:
    """
    Normalize and validate contract financial information.

    Returns:
        The normalized total amount and remaining amount due.

    Raises:
        ValueError: If an amount is invalid or inconsistent.
    """

    normalized_total_amount = _normalize_amount(
        value=total_amount,
        field_name="Total amount",
    )

    normalized_amount_due = _normalize_amount(
        value=amount_due,
        field_name="Amount due",
    )

    if normalized_total_amount <= 0:
        raise ValueError(
            "Total amount must be greater than zero."
        )

    if normalized_amount_due < 0:
        raise ValueError(
            "Amount due cannot be negative."
        )

    if normalized_amount_due > normalized_total_amount:
        raise ValueError(
            "Amount due cannot exceed total amount."
        )

    return (
        normalized_total_amount,
        normalized_amount_due,
    )


def _validate_signed_status(
    is_signed: bool,
) -> bool:
    """
    Validate the contract signature status.

    Returns:
        The validated Boolean signature status.

    Raises:
        ValueError: If the provided value is not a Boolean.
    """

    if not isinstance(is_signed, bool):
        raise ValueError(
            "Signed status must be a Boolean."
        )

    return is_signed


def _get_client_by_id(
    client_id: int,
) -> Client:
    """
    Retrieve a client by identifier.

    Returns:
        The matching client.

    Raises:
        ValueError: If no client matches the provided identifier.
    """

    client = Client.get_or_none(
        Client.id == client_id
    )

    if client is None:
        raise ValueError("Client not found.")

    return client


def _get_contract_by_id(
    contract_id: int,
) -> Contract:
    """
    Retrieve a contract by identifier.

    Returns:
        The matching contract.

    Raises:
        ValueError: If no contract matches the provided identifier.
    """

    contract = Contract.get_or_none(
        Contract.id == contract_id
    )

    if contract is None:
        raise ValueError("Contract not found.")

    return contract


def _ensure_contract_update_permission(
    contract: Contract,
    current_user: User,
) -> None:
    """
    Verify that the current user may update the selected contract.

    Management users may update every contract. Commercial users may
    only update contracts belonging to clients for whom they are
    responsible.

    Raises:
        PermissionError: If the current user is not authorized.
    """

    if has_required_permission(
        current_user,
        "MANAGEMENT",
    ):
        return

    if (
        has_required_permission(
            current_user,
            "COMMERCIAL",
        )
        and contract.client.sales_contact_id == current_user.id
    ):
        return

    raise PermissionError(
        "You can only update contracts for your own clients."
    )


def create_contract(
    client_id: int,
    total_amount: Decimal | int | float | str,
    amount_due: Decimal | int | float | str,
    is_signed: bool,
    current_user: User,
) -> Contract:
    """
    Create a new contract.

    Only an authenticated and active management user may create a
    contract. The contract is automatically associated with the
    commercial user responsible for the selected client.

    Returns:
        The newly created contract.

    Raises:
        PermissionError: If the current user is not authorized.
        ValueError: If the client does not exist or the contract data
        is invalid.
    """

    require_permission(
        current_user,
        "MANAGEMENT",
    )

    client = _get_client_by_id(
        client_id=client_id,
    )

    normalized_total_amount, normalized_amount_due = (
        _validate_contract_amounts(
            total_amount=total_amount,
            amount_due=amount_due,
        )
    )

    validated_is_signed = _validate_signed_status(
        is_signed=is_signed,
    )

    return Contract.create(
        client=client,
        sales_contact=client.sales_contact,
        total_amount=normalized_total_amount,
        amount_due=normalized_amount_due,
        is_signed=validated_is_signed,
    )


def list_all_contracts(
    current_user: User,
) -> list[Contract]:
    """
    Retrieve every contract stored in the CRM.

    All authenticated and active collaborators may consult every
    contract in read-only mode.

    Returns:
        A list of contracts ordered by creation date and identifier.

    Raises:
        PermissionError: If the current user is not authorized.
    """

    require_permission(
        current_user,
        *CONTRACT_READ_DEPARTMENTS,
    )

    return list(
        Contract.select().order_by(
            Contract.created_at,
            Contract.id,
        )
    )


def list_unsigned_contracts(
    current_user: User,
) -> list[Contract]:
    """
    Retrieve contracts that have not yet been signed.

    This filter is available to authenticated and active commercial
    users.

    Returns:
        A list of unsigned contracts ordered by creation date and
        identifier.

    Raises:
        PermissionError: If the current user is not authorized.
    """

    require_permission(
        current_user,
        "COMMERCIAL",
    )

    return list(
        Contract.select()
        .where(~Contract.is_signed)
        .order_by(
            Contract.created_at,
            Contract.id,
        )
    )


def list_unpaid_contracts(
    current_user: User,
) -> list[Contract]:
    """
    Retrieve contracts that have not yet been fully paid.

    This filter is available to authenticated and active commercial
    users.

    Returns:
        A list of contracts with a remaining amount due, ordered by
        creation date and identifier.

    Raises:
        PermissionError: If the current user is not authorized.
    """

    require_permission(
        current_user,
        "COMMERCIAL",
    )

    return list(
        Contract.select()
        .where(Contract.amount_due > 0)
        .order_by(
            Contract.created_at,
            Contract.id,
        )
    )


def update_contract(
    contract_id: int,
    total_amount: Decimal | int | float | str,
    amount_due: Decimal | int | float | str,
    is_signed: bool,
    current_user: User,
) -> Contract:
    """
    Update an existing contract.

    Management users may update every contract. Commercial users may
    only update contracts belonging to clients for whom they are
    responsible.

    The contract sales contact is synchronized with the commercial
    user currently assigned to the related client.

    Returns:
        The updated contract.

    Raises:
        PermissionError: If the current user is not authorized.
        ValueError: If the contract does not exist or the contract data
        is invalid.
    """

    require_permission(
        current_user,
        "MANAGEMENT",
        "COMMERCIAL",
    )

    contract = _get_contract_by_id(
        contract_id=contract_id,
    )

    _ensure_contract_update_permission(
        contract=contract,
        current_user=current_user,
    )

    normalized_total_amount, normalized_amount_due = (
        _validate_contract_amounts(
            total_amount=total_amount,
            amount_due=amount_due,
        )
    )

    validated_is_signed = _validate_signed_status(
        is_signed=is_signed,
    )

    contract.sales_contact = contract.client.sales_contact
    contract.total_amount = normalized_total_amount
    contract.amount_due = normalized_amount_due
    contract.is_signed = validated_is_signed

    contract.save(
        only=[
            Contract.sales_contact,
            Contract.total_amount,
            Contract.amount_due,
            Contract.is_signed,
        ]
    )

    return contract
