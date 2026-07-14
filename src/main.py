"""
main.py

Role:
- Define the application's command-line interface.
- Collect user input from the terminal.
- Delegate business logic to dedicated service modules.
- Display execution results to the user.

Business rules are not implemented in this module.
"""

import typer

from src.auth import (
    authenticate_user,
    require_permission,
)
from src.services.client_service import (
    create_client,
    list_all_clients,
    update_client,
)

from src.services.user_service import (
    create_initial_management_user,
    create_user,
    delete_user,
    update_user,
)

from src.database import database

from src.models.client import Client
from src.models.contract import Contract
from src.models.event import Event
from src.models.user import User


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


if __name__ == "__main__":
    app()