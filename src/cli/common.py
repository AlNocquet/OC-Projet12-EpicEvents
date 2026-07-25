"""
Shared helpers used by CLI command modules.
"""

import typer

from src.core.auth import authenticate_user
from src.models.user import User
from src.core.jwt_auth import get_current_user_from_token


def prompt_password(
    prompt_text: str,
    confirmation: bool = False,
) -> str:
    """Securely collect a password from the terminal."""

    return typer.prompt(
        prompt_text,
        hide_input=True,
        confirmation_prompt=confirmation,
    )


def authenticate_current_user(
    email: str,
) -> User:
    """Authenticate the collaborator currently using the CLI."""

    password = prompt_password(
        prompt_text="Password",
    )

    try:
        user = authenticate_user(
            email=email,
            password=password,
        )

    except ValueError as error:
        typer.echo(str(error))
        raise typer.Exit(code=1) from error

    if user is None:
        typer.echo("Authentication failed.")
        raise typer.Exit(code=1)

    return user


def get_current_user_from_session() -> User:
    """Return the active collaborator identified by the local JWT."""

    try:
        return get_current_user_from_token()

    except ValueError as error:
        typer.echo(str(error))
        raise typer.Exit(code=1) from error