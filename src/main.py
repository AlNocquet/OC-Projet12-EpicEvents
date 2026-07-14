"""
main.py

Role:
- Define the application's command-line interface.
- Collect user input from the terminal.
- Delegate business logic to dedicated service modules.
- Display execution results to the user.

Business rules are not implemented in this module.
"""

from datetime import datetime

import typer

from src.auth import (
    authenticate_user,
    require_permission,
)
from src.database import database
from src.models.client import Client
from src.models.contract import Contract
from src.models.event import Event
from src.models.user import User
from src.services.client_service import (
    create_client,
    list_all_clients,
    update_client,
)
from src.services.contract_service import (
    create_contract,
    list_all_contracts,
    list_unpaid_contracts,
    list_unsigned_contracts,
    update_contract,
)
from src.services.event_service import (
    assign_support_to_event,
    create_event,
    list_all_events,
    list_my_support_events,
    list_unassigned_events,
    update_event,
)
from src.services.user_service import (
    create_initial_management_user,
    create_user,
    delete_user,
    update_user,
)


app = typer.Typer()


def _prompt_password(
    prompt_text: str,
    confirmation: bool = False,
) -> str:
    """
    Securely collect a password from the terminal.

    The password is hidden and is never supplied as a command-line
    argument.
    """

    return typer.prompt(
        prompt_text,
        hide_input=True,
        confirmation_prompt=confirmation,
    )


def _authenticate_current_user(
    email: str,
) -> User:
    """
    Authenticate the current CLI user.

    Securely prompts for the password and returns the authenticated
    active user.

    Raises:
        typer.Exit: If authentication fails.
    """

    password = _prompt_password(
        prompt_text="Password",
    )

    try:
        user = authenticate_user(
            email=email,
            password=password,
        )

    except ValueError as error:
        typer.echo(str(error))
        raise typer.Exit(code=1)

    if user is None:
        typer.echo("Authentication failed.")
        raise typer.Exit(code=1)

    return user


def _display_contracts(
    contracts: list[Contract],
) -> None:
    """
    Display a collection of contracts in the terminal.
    """

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


def _parse_datetime(
    value: str,
    field_name: str,
) -> datetime:
    """
    Parse an ISO-formatted datetime supplied through the CLI.

    Accepted examples include ``2026-07-20T14:30`` and
    ``2026-07-20 14:30``.

    Raises:
        ValueError: If the value cannot be parsed.
    """

    try:
        return datetime.fromisoformat(
            value.strip(),
        )

    except (TypeError, ValueError):
        raise ValueError(
            f"{field_name} must use ISO format "
            "YYYY-MM-DDTHH:MM."
        )


def _display_events(
    events: list[Event],
) -> None:
    """
    Display a collection of events in the terminal.
    """

    if not events:
        typer.echo("No events found.")
        return

    for event in events:
        support_name = (
            event.support_contact.full_name
            if event.support_contact_id is not None
            else "Unassigned"
        )

        typer.echo(
            f"ID: {event.id} | "
            f"Event: {event.event_name} | "
            f"Contract: {event.contract.id} | "
            f"Client: {event.contract.client.full_name} | "
            f"Support: {support_name} | "
            f"Location: {event.location} | "
            f"Attendees: {event.attendees} | "
            f"Start: {event.event_start:%Y-%m-%d %H:%M} | "
            f"End: {event.event_end:%Y-%m-%d %H:%M} | "
            f"Notes: {event.notes or '-'}"
        )


@app.command()
def initialize_database() -> None:
    """
    Initialize the application database.

    Creates all database tables required by the CRM application.
    This command should be executed before the first application use.
    """

    database.connect(reuse_if_open=True)

    try:
        database.create_tables(
            [
                User,
                Client,
                Contract,
                Event,
            ],
            safe=True,
        )

        typer.echo(
            "Database initialized successfully."
        )

    finally:
        if not database.is_closed():
            database.close()


@app.command()
def authenticate_user_command(
    email: str,
) -> None:
    """
    Authenticate an active collaborator.
    """

    user = _authenticate_current_user(
        email=email,
    )

    typer.echo(
        f"Welcome {user.full_name}!"
    )


@app.command()
def create_initial_management_user_command(
    full_name: str,
    email: str,
) -> None:
    """
    Create the first management account.

    This command may only be used while the database contains no
    collaborator.
    """

    password = _prompt_password(
        prompt_text="Management password",
        confirmation=True,
    )

    try:
        user = create_initial_management_user(
            full_name=full_name,
            email=email,
            password=password,
        )

        typer.echo(
            "Initial management user created successfully. "
            f"User ID: {user.id}."
        )

    except (ValueError, PermissionError) as error:
        typer.echo(str(error))
        raise typer.Exit(code=1)


@app.command()
def create_user_account_command(
    authenticated_email: str,
    full_name: str,
    email: str,
    department: str,
) -> None:
    """
    Create a collaborator account.

    Only an authenticated and active management user may create a
    collaborator.
    """

    current_user = _authenticate_current_user(
        email=authenticated_email,
    )

    password = _prompt_password(
        prompt_text="New user password",
        confirmation=True,
    )

    try:
        user = create_user(
            full_name=full_name,
            email=email,
            password=password,
            department=department,
            current_user=current_user,
        )

        typer.echo(
            f"User created successfully. User ID: {user.id}."
        )

    except (ValueError, PermissionError) as error:
        typer.echo(str(error))
        raise typer.Exit(code=1)


@app.command()
def update_user_account_command(
    authenticated_email: str,
    user_id: int,
    full_name: str,
    email: str,
    department: str,
) -> None:
    """
    Update a collaborator account.

    Only an authenticated and active management user may update a
    collaborator.
    """

    current_user = _authenticate_current_user(
        email=authenticated_email,
    )

    try:
        user = update_user(
            user_id=user_id,
            full_name=full_name,
            email=email,
            department=department,
            current_user=current_user,
        )

        typer.echo(
            f"User {user.id} updated successfully."
        )

    except (ValueError, PermissionError) as error:
        typer.echo(str(error))
        raise typer.Exit(code=1)


@app.command()
def delete_user_account_command(
    authenticated_email: str,
    user_id: int,
) -> None:
    """
    Delete a collaborator account.

    Only an authenticated and active management user may delete a
    collaborator. The account is deactivated to preserve related CRM
    records.
    """

    current_user = _authenticate_current_user(
        email=authenticated_email,
    )

    try:
        user = delete_user(
            user_id=user_id,
            current_user=current_user,
        )

        typer.echo(
            f"User {user.id} deleted successfully."
        )

    except (ValueError, PermissionError) as error:
        typer.echo(str(error))
        raise typer.Exit(code=1)


@app.command()
def check_management_access_command(
    email: str,
) -> None:
    """
    Verify that an active user belongs to the management department.
    """

    user = _authenticate_current_user(
        email=email,
    )

    try:
        require_permission(
            user,
            "MANAGEMENT",
        )

        typer.echo("Access granted.")

    except PermissionError as error:
        typer.echo(str(error))
        raise typer.Exit(code=1)


@app.command()
def create_client_command(
    authenticated_email: str,
    full_name: str,
    client_email: str,
    phone: str,
    company_name: str,
) -> None:
    """
    Create a new client.

    Only an authenticated and active commercial user may create a
    client. The client is automatically assigned to that commercial.
    """

    current_user = _authenticate_current_user(
        email=authenticated_email,
    )

    try:
        client = create_client(
            full_name=full_name,
            email=client_email,
            phone=phone,
            company_name=company_name,
            current_user=current_user,
        )

        typer.echo(
            "Client created successfully. "
            f"Client ID: {client.id}."
        )

    except (ValueError, PermissionError) as error:
        typer.echo(str(error))
        raise typer.Exit(code=1)


@app.command()
def list_clients_command(
    authenticated_email: str,
) -> None:
    """
    Display every client stored in the CRM.

    All authenticated and active collaborators may consult client
    information in read-only mode.
    """

    current_user = _authenticate_current_user(
        email=authenticated_email,
    )

    try:
        clients = list_all_clients(
            current_user=current_user,
        )

    except PermissionError as error:
        typer.echo(str(error))
        raise typer.Exit(code=1)

    if not clients:
        typer.echo("No clients found.")
        return

    for client in clients:
        typer.echo(
            f"ID: {client.id} | "
            f"Name: {client.full_name} | "
            f"Email: {client.email} | "
            f"Phone: {client.phone} | "
            f"Company: {client.company_name} | "
            f"Sales contact: {client.sales_contact.full_name} | "
            f"Created: {client.created_at:%Y-%m-%d %H:%M} | "
            f"Updated: {client.updated_at:%Y-%m-%d %H:%M}"
        )


@app.command()
def update_client_command(
    authenticated_email: str,
    client_id: int,
    full_name: str,
    client_email: str,
    phone: str,
    company_name: str,
) -> None:
    """
    Update an existing client.

    Only the authenticated and active commercial assigned to the client
    may update its information.
    """

    current_user = _authenticate_current_user(
        email=authenticated_email,
    )

    try:
        client = update_client(
            client_id=client_id,
            full_name=full_name,
            email=client_email,
            phone=phone,
            company_name=company_name,
            current_user=current_user,
        )

        typer.echo(
            f"Client {client.id} updated successfully."
        )

    except (ValueError, PermissionError) as error:
        typer.echo(str(error))
        raise typer.Exit(code=1)


@app.command()
def create_contract_command(
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

    current_user = _authenticate_current_user(
        email=authenticated_email,
    )

    try:
        contract = create_contract(
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
        raise typer.Exit(code=1)


@app.command()
def list_contracts_command(
    authenticated_email: str,
) -> None:
    """
    Display every contract stored in the CRM.

    All authenticated and active collaborators may consult contract
    information in read-only mode.
    """

    current_user = _authenticate_current_user(
        email=authenticated_email,
    )

    try:
        contracts = list_all_contracts(
            current_user=current_user,
        )

    except PermissionError as error:
        typer.echo(str(error))
        raise typer.Exit(code=1)

    _display_contracts(
        contracts=contracts,
    )


@app.command()
def list_unsigned_contracts_command(
    authenticated_email: str,
) -> None:
    """
    Display every unsigned contract.

    This filter is available only to authenticated and active
    commercial users.
    """

    current_user = _authenticate_current_user(
        email=authenticated_email,
    )

    try:
        contracts = list_unsigned_contracts(
            current_user=current_user,
        )

    except PermissionError as error:
        typer.echo(str(error))
        raise typer.Exit(code=1)

    _display_contracts(
        contracts=contracts,
    )


@app.command()
def list_unpaid_contracts_command(
    authenticated_email: str,
) -> None:
    """
    Display every contract that has not yet been fully paid.

    This filter is available only to authenticated and active
    commercial users.
    """

    current_user = _authenticate_current_user(
        email=authenticated_email,
    )

    try:
        contracts = list_unpaid_contracts(
            current_user=current_user,
        )

    except PermissionError as error:
        typer.echo(str(error))
        raise typer.Exit(code=1)

    _display_contracts(
        contracts=contracts,
    )


@app.command()
def update_contract_command(
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

    current_user = _authenticate_current_user(
        email=authenticated_email,
    )

    try:
        contract = update_contract(
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
        raise typer.Exit(code=1)




@app.command()
def create_event_command(
    authenticated_email: str,
    contract_id: int,
    event_name: str,
    location: str,
    attendees: int,
    event_start: str,
    event_end: str,
    notes: str = "",
) -> None:
    """
    Create an event for a signed contract.

    Only the authenticated commercial collaborator responsible for the
    related client may create the event. Datetimes must use ISO format.
    """

    current_user = _authenticate_current_user(
        email=authenticated_email,
    )

    try:
        parsed_event_start = _parse_datetime(
            value=event_start,
            field_name="Event start",
        )
        parsed_event_end = _parse_datetime(
            value=event_end,
            field_name="Event end",
        )

        event = create_event(
            contract_id=contract_id,
            event_name=event_name,
            location=location,
            attendees=attendees,
            event_start=parsed_event_start,
            event_end=parsed_event_end,
            notes=notes,
            current_user=current_user,
        )

        typer.echo(
            "Event created successfully. "
            f"Event ID: {event.id}."
        )

    except (ValueError, PermissionError) as error:
        typer.echo(str(error))
        raise typer.Exit(code=1)


@app.command()
def list_events_command(
    authenticated_email: str,
) -> None:
    """
    Display every event stored in the CRM.

    All authenticated and active collaborators may consult events in
    read-only mode.
    """

    current_user = _authenticate_current_user(
        email=authenticated_email,
    )

    try:
        events = list_all_events(
            current_user=current_user,
        )

    except PermissionError as error:
        typer.echo(str(error))
        raise typer.Exit(code=1)

    _display_events(
        events=events,
    )


@app.command()
def list_unassigned_events_command(
    authenticated_email: str,
) -> None:
    """
    Display events without an assigned support collaborator.

    This filter is available only to authenticated and active management
    collaborators.
    """

    current_user = _authenticate_current_user(
        email=authenticated_email,
    )

    try:
        events = list_unassigned_events(
            current_user=current_user,
        )

    except PermissionError as error:
        typer.echo(str(error))
        raise typer.Exit(code=1)

    _display_events(
        events=events,
    )


@app.command()
def list_my_events_command(
    authenticated_email: str,
) -> None:
    """
    Display events assigned to the authenticated support collaborator.
    """

    current_user = _authenticate_current_user(
        email=authenticated_email,
    )

    try:
        events = list_my_support_events(
            current_user=current_user,
        )

    except PermissionError as error:
        typer.echo(str(error))
        raise typer.Exit(code=1)

    _display_events(
        events=events,
    )


@app.command()
def assign_support_to_event_command(
    authenticated_email: str,
    event_id: int,
    support_user_id: int,
) -> None:
    """
    Assign an active support collaborator to an event.

    Only an authenticated and active management collaborator may assign
    the support contact.
    """

    current_user = _authenticate_current_user(
        email=authenticated_email,
    )

    try:
        event = assign_support_to_event(
            event_id=event_id,
            support_user_id=support_user_id,
            current_user=current_user,
        )

        typer.echo(
            f"Support collaborator assigned to event {event.id}."
        )

    except (ValueError, PermissionError) as error:
        typer.echo(str(error))
        raise typer.Exit(code=1)


@app.command()
def update_event_command(
    authenticated_email: str,
    event_id: int,
    event_name: str,
    location: str,
    attendees: int,
    event_start: str,
    event_end: str,
    notes: str = "",
) -> None:
    """
    Update an event assigned to the authenticated support collaborator.

    Datetimes must use ISO format.
    """

    current_user = _authenticate_current_user(
        email=authenticated_email,
    )

    try:
        parsed_event_start = _parse_datetime(
            value=event_start,
            field_name="Event start",
        )
        parsed_event_end = _parse_datetime(
            value=event_end,
            field_name="Event end",
        )

        event = update_event(
            event_id=event_id,
            event_name=event_name,
            location=location,
            attendees=attendees,
            event_start=parsed_event_start,
            event_end=parsed_event_end,
            notes=notes,
            current_user=current_user,
        )

        typer.echo(
            f"Event {event.id} updated successfully."
        )

    except (ValueError, PermissionError) as error:
        typer.echo(str(error))
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()