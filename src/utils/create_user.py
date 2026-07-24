"""
Create the first management collaborator.

Run from the project root with:

    python -m src.utils.create_user
"""

import typer

from src.services.user_service import (
    create_initial_management_user,
)


def create_initial_user(
    full_name: str,
    email: str,
) -> None:
    """
    Create the first management account.

    This script may only be used while the database contains no
    collaborator.
    """

    password = typer.prompt(
        "Management password",
        hide_input=True,
        confirmation_prompt=True,
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
        raise typer.Exit(code=1) from error


if __name__ == "__main__":
    typer.run(create_initial_user)
