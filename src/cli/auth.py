"""
CLI commands related to authentication and access checks.

The login command currently verifies credentials. JWT token creation
will be added in the next authentication refactoring step.
"""

import typer

from src.cli.common import authenticate_current_user
from src.core.auth import require_permission


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

    typer.echo(
        f"Welcome {user.full_name}!"
    )


@app.command("check-management")
def check_management(
    email: str,
) -> None:
    """Verify that an active user belongs to management."""

    user = authenticate_current_user(
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
        raise typer.Exit(code=1) from error
