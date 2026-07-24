"""
CLI commands used to manage CRM clients.
"""

import typer

from src.cli.common import authenticate_current_user
from src.services.client_service import (
    create_client as create_client_service,
    list_all_clients as list_all_clients_service,
    update_client as update_client_service,
)


app = typer.Typer(
    help="Manage CRM clients.",
    no_args_is_help=True,
)


@app.command("create")
def create(
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

    current_user = authenticate_current_user(
        email=authenticated_email,
    )

    try:
        client = create_client_service(
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
        raise typer.Exit(code=1) from error


@app.command("list")
def list_clients(
    authenticated_email: str,
) -> None:
    """
    Display every client stored in the CRM.

    All authenticated and active collaborators may consult client
    information in read-only mode.
    """

    current_user = authenticate_current_user(
        email=authenticated_email,
    )

    try:
        clients = list_all_clients_service(
            current_user=current_user,
        )

    except PermissionError as error:
        typer.echo(str(error))
        raise typer.Exit(code=1) from error

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


@app.command("update")
def update(
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

    current_user = authenticate_current_user(
        email=authenticated_email,
    )

    try:
        client = update_client_service(
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
        raise typer.Exit(code=1) from error