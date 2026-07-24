"""
CLI commands used to demonstrate application monitoring.
"""

import typer

from src.cli.common import authenticate_current_user
from src.core.auth import require_permission
from src.core.monitoring import (
    initialize_sentry,
    send_test_exception,
)


app = typer.Typer(
    help="Manage application monitoring demonstrations.",
    no_args_is_help=True,
)


@app.command("test-sentry")
def test_sentry(
    authenticated_email: str,
) -> None:
    """Send a controlled exception to Sentry."""

    current_user = authenticate_current_user(
        email=authenticated_email,
    )

    try:
        require_permission(
            current_user,
            "MANAGEMENT",
        )

    except PermissionError as error:
        typer.echo(str(error))
        raise typer.Exit(code=1) from error

    if not initialize_sentry():
        typer.echo(
            "Sentry is not configured. "
            "Set the SENTRY_DSN environment variable."
        )
        raise typer.Exit(code=1)

    event_id = send_test_exception()

    if event_id is None:
        typer.echo(
            "The Sentry test exception could not be sent."
        )
        raise typer.Exit(code=1)

    typer.echo(
        "Sentry test exception sent successfully. "
        f"Event ID: {event_id}."
    )
