"""
CLI commands used to manage CRM contracts.
"""

import typer

from src.cli.common import authenticate_current_user
from src.models.contract import Contract
from src.services.contract_service import (
    create_contract as create_contract_service,
    list_all_contracts as list_all_contracts_service,
    list_unpaid_contracts as list_unpaid_contracts_service,
    list_unsigned_contracts as list_unsigned_contracts_service,
    update_contract as update_contract_service,
)


app = typer.Typer(
    help="Manage CRM contracts.",
    no_args_is_help=True,
)


def _display_contracts(
    contracts: list[Contract],
) -> None:
    """Display a collection of contracts in the terminal."""

    if not contracts:
        typer.echo("No contracts found.")
        return

    for contract in contracts:
        typer.echo(
            f"ID: {contract.id} | "
            f"Client: {contract.client.full_name} | "
            f"Company: {contract.client.company_name} | "
            f"Sales contact: {contract.sales_contact.full_name} | "
            f"Total amount: {contract.total_amount:.2f} | "
            f"Amount due: {contract.amount_due:.2f} | "
            f"Signed: {'Yes' if contract.is_signed else 'No'} | "
            f"Created: {contract.created_at:%Y-%m-%d %H:%M}"
        )


@app.command("create")
def create(
    authenticated_email: str,
    client_id: int,
    total_amount: str,
    amount_due: str,
    is_signed: bool,
) -> None:
    """
    Create a new contract.

    Only an authenticated and active management user may create a
    contract. The commercial responsible for the client is
    automatically assigned to the contract.

    The signed status must be provided as true or false.
    """

    current_user = authenticate_current_user(
        email=authenticated_email,
    )

    try:
        contract = create_contract_service(
            client_id=client_id,
            total_amount=total_amount,
            amount_due=amount_due,
            is_signed=is_signed,
            current_user=current_user,
        )

        typer.echo(
            "Contract created successfully. "
            f"Contract ID: {contract.id}."
        )

    except (ValueError, PermissionError) as error:
        typer.echo(str(error))
        raise typer.Exit(code=1) from error


@app.command("list")
def list_contracts(
    authenticated_email: str,
) -> None:
    """
    Display every contract stored in the CRM.

    All authenticated and active collaborators may consult contract
    information in read-only mode.
    """

    current_user = authenticate_current_user(
        email=authenticated_email,
    )

    try:
        contracts = list_all_contracts_service(
            current_user=current_user,
        )

    except PermissionError as error:
        typer.echo(str(error))
        raise typer.Exit(code=1) from error

    _display_contracts(
        contracts=contracts,
    )


@app.command("list-unsigned")
def list_unsigned(
    authenticated_email: str,
) -> None:
    """
    Display every unsigned contract.

    This filter is available only to authenticated and active
    commercial users.
    """

    current_user = authenticate_current_user(
        email=authenticated_email,
    )

    try:
        contracts = list_unsigned_contracts_service(
            current_user=current_user,
        )

    except PermissionError as error:
        typer.echo(str(error))
        raise typer.Exit(code=1) from error

    _display_contracts(
        contracts=contracts,
    )


@app.command("list-unpaid")
def list_unpaid(
    authenticated_email: str,
) -> None:
    """
    Display every contract that has not yet been fully paid.

    This filter is available only to authenticated and active
    commercial users.
    """

    current_user = authenticate_current_user(
        email=authenticated_email,
    )

    try:
        contracts = list_unpaid_contracts_service(
            current_user=current_user,
        )

    except PermissionError as error:
        typer.echo(str(error))
        raise typer.Exit(code=1) from error

    _display_contracts(
        contracts=contracts,
    )


@app.command("update")
def update(
    authenticated_email: str,
    contract_id: int,
    total_amount: str,
    amount_due: str,
    is_signed: bool,
) -> None:
    """
    Update an existing contract.

    Management users may update every contract. Commercial users may
    update only contracts belonging to clients for whom they are
    responsible.

    The signed status must be provided as true or false.
    """

    current_user = authenticate_current_user(
        email=authenticated_email,
    )

    try:
        contract = update_contract_service(
            contract_id=contract_id,
            total_amount=total_amount,
            amount_due=amount_due,
            is_signed=is_signed,
            current_user=current_user,
        )

        typer.echo(
            f"Contract {contract.id} updated successfully."
        )

    except (ValueError, PermissionError) as error:
        typer.echo(str(error))
        raise typer.Exit(code=1) from error