"""
main.py

Role:
- Define the application's command-line interface.
- Collect user input from the terminal.
- Delegate business logic to dedicated service modules.
- Display execution results to the user.

Business rules and database logic must not be implemented in this module.
"""

import typer

from src.database import database

from src.models.user import User
from src.models.client import Client
from src.models.contract import Contract
from src.models.event import Event

from src.auth import (
    authenticate_user,
    require_permission,
)

from src.user_service import create_user

app = typer.Typer()


@app.command()
def initialize_database():
    """
    Initialize the application database.

    Creates all database tables required by the CRM application.
    This command should be executed before the first application use.
    """

    database.connect()

    database.create_tables(
        [
            User,
            Client,
            Contract,
            Event,
        ]
    )

    database.close()

    typer.echo("Database initialized successfully.")


@app.command()
def authenticate_user_command(
    email: str,
    password: str,
):
    """
    Authenticate a user.

    Validates the provided credentials and grants access only if the
    authentication succeeds.
    """

    try:
        user = authenticate_user(
            email=email,
            password=password,
        )

    except ValueError as error:
        typer.echo(str(error))
        raise typer.Exit(code=1)

    if user:
        typer.echo(f"Welcome {user.full_name}!")
    else:
        typer.echo("Authentication failed.")


@app.command()
def create_user_account_command(
    full_name: str,
    email: str,
    password: str,
    department: str,
):
    """
    Create a new user account.

    Validates the provided information and delegates the user creation
    process to the dedicated service layer.
    """

    try:
        create_user(
            full_name=full_name,
            email=email,
            password=password,
            department=department,
        )

        typer.echo("User created successfully.")

    except ValueError as error:
        typer.echo(str(error))
        raise typer.Exit(code=1)


@app.command()
def check_management_access_command(
    email: str,
    password: str,
):
    """
    Verify management permissions.

    Authenticates the user and checks whether the account belongs to
    the management department.
    """

    try:
        user = authenticate_user(
            email=email,
            password=password,
        )

    except ValueError as error:
        typer.echo(str(error))
        raise typer.Exit(code=1)

    if not user:
        typer.echo("Authentication failed.")
        raise typer.Exit(code=1)

    try:
        require_permission(
            user,
            "MANAGEMENT",
        )

        typer.echo("Access granted.")

    except PermissionError as error:
        typer.echo(str(error))
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()