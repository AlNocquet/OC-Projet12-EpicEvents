"""
CLI commands used to manage collaborator accounts.
"""

import typer

from src.cli.common import (
    authenticate_current_user,
    prompt_password,
)
from src.services.user_service import (
    create_user as create_user_service,
    delete_user as delete_user_service,
    update_user as update_user_service,
)


app = typer.Typer(
    help="Manage collaborator accounts.",
    no_args_is_help=True,
)


@app.command("create")
def create(
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

    current_user = authenticate_current_user(
        email=authenticated_email,
    )

    password = prompt_password(
        prompt_text="New user password",
        confirmation=True,
    )

    try:
        user = create_user_service(
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
        raise typer.Exit(code=1) from error


@app.command("update")
def update(
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

    current_user = authenticate_current_user(
        email=authenticated_email,
    )

    try:
        user = update_user_service(
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
        raise typer.Exit(code=1) from error


@app.command("delete")
def delete(
    authenticated_email: str,
    user_id: int,
) -> None:
    """
    Deactivate a collaborator account.

    Related CRM records are preserved.
    """

    current_user = authenticate_current_user(
        email=authenticated_email,
    )

    try:
        user = delete_user_service(
            user_id=user_id,
            current_user=current_user,
        )

        typer.echo(
            f"User {user.id} deleted successfully."
        )

    except (ValueError, PermissionError) as error:
        typer.echo(str(error))
        raise typer.Exit(code=1) from error