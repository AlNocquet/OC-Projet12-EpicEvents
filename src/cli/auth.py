"""
CLI commands related to authentication and access checks.

The login command currently verifies credentials. JWT token creation
will be added in the next authentication refactoring step.
"""

import typer

from src.cli.common import authenticate_current_user
from src.core.auth import require_permission
from src.core.jwt_auth import create_access_token, save_token
from src.cli.common import get_current_user_from_session

from src.core.jwt_auth import (
    create_access_token,
    delete_token,
    save_token,
)


app = typer.Typer(
    help="Authenticate collaborators and verify access.",
    no_args_is_help=True,
)


@app.command("login")
def login(
    email: str,
) -> None:
    """Authenticate an active collaborator."""

    user = authenticate_current_user(
        email=email,
    )

    token = create_access_token(
    user=user,
    )

    save_token(
        token=token,
    )

    typer.echo(
        f"Welcome {user.full_name}!"
    )


@app.command("logout")
def logout() -> None:
    """Delete the locally stored JWT session."""

    if delete_token():
        typer.echo("Logout successful.")
        return

    typer.echo("No active session found.")

    
@app.command("check-management")
def check_management() -> None:
    """Verify that the authenticated user belongs to management."""

    user = get_current_user_from_session()

    try:
        require_permission(
            user,
            "MANAGEMENT",
        )

        typer.echo("Access granted.")

    except PermissionError as error:
        typer.echo(str(error))
        raise typer.Exit(code=1) from error
