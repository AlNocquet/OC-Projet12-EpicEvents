"""
Epic Events command-line application entry point.

This module only initializes the CLI applications, monitoring, and the
application execution.
"""

import typer

from src.cli import auth as auth_cli
from src.cli import client as client_cli
from src.cli import contract as contract_cli
from src.cli import event as event_cli
from src.cli import monitoring as monitoring_cli
from src.cli import user as user_cli

from src.core.monitoring import (
    capture_application_exception,
    initialize_sentry,
)


app = typer.Typer(
    help="Epic Events secure CRM.",
    no_args_is_help=True,
)

app.add_typer(
    auth_cli.app,
    name="auth",
)

app.add_typer(
    user_cli.app,
    name="user",
)

app.add_typer(
    client_cli.app,
    name="client",
)

app.add_typer(
    contract_cli.app,
    name="contract",
)

app.add_typer(
    event_cli.app,
    name="event",
)

app.add_typer(
    monitoring_cli.app,
    name="monitoring",
)


def run_app() -> None:
    """Initialize monitoring and run the Typer application."""

    initialize_sentry()

    try:
        app()

    except Exception as error:
        event_id = capture_application_exception(
            error=error,
        )

        typer.echo(
            "An unexpected application error occurred."
        )

        if event_id is not None:
            typer.echo(
                f"Sentry event ID: {event_id}."
            )

        raise SystemExit(1) from error


if __name__ == "__main__":
    run_app()
