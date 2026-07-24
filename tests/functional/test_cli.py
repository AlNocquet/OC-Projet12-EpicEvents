"""
Functional tests for the Epic Events Typer command-line interface.
"""

from typer.testing import CliRunner

from src.__main__ import app


runner = CliRunner()


def test_cli_help_displays_main_commands():
    """The CLI help exposes the main CRM command groups."""

    result = runner.invoke(
        app,
        [
            "--help",
        ],
    )

    assert result.exit_code == 0
    assert "auth" in result.stdout
    assert "user" in result.stdout
    assert "client" in result.stdout
    assert "contract" in result.stdout
    assert "event" in result.stdout
    assert "monitoring" in result.stdout


def test_cli_authentication_success(
    management_user,
):
    """Valid credentials authenticate a collaborator through the CLI."""

    result = runner.invoke(
        app,
        [
            "auth",
            "login",
            management_user.email,
        ],
        input="ManagementPassword123!\n",
    )

    assert result.exit_code == 0
    assert "Welcome Morgan Manager!" in result.stdout


def test_cli_authentication_failure(
    management_user,
):
    """Invalid credentials are rejected through the CLI."""

    result = runner.invoke(
        app,
        [
            "auth",
            "login",
            management_user.email,
        ],
        input="WrongPassword123!\n",
    )

    assert result.exit_code == 1
    assert "Authentication failed." in result.stdout


def test_cli_list_clients_for_authenticated_support(
    support_user,
    client,
):
    """An authenticated support collaborator can consult clients."""

    result = runner.invoke(
        app,
        [
            "client",
            "list",
            support_user.email,
        ],
        input="SupportPassword123!\n",
    )

    assert result.exit_code == 0
    assert "Kevin Casey" in result.stdout
    assert "Cool Startup LLC" in result.stdout


def test_cli_management_cannot_create_client(
    management_user,
):
    """CLI operations enforce service-layer permissions."""

    result = runner.invoke(
        app,
        [
            "client",
            "create",
            management_user.email,
            "Unauthorized Client",
            "unauthorized@example.com",
            "+33 1 23 45 67 89",
            "Unauthorized Company",
        ],
        input="ManagementPassword123!\n",
    )

    assert result.exit_code == 1
    assert "Permission denied." in result.stdout


def test_cli_event_creation_rejects_invalid_datetime(
    commercial_user,
    signed_contract,
):
    """Invalid date input is rejected before event persistence."""

    result = runner.invoke(
        app,
        [
            "event",
            "create",
            commercial_user.email,
            str(signed_contract.id),
            "Conference",
            "Paris",
            "100",
            "invalid-date",
            "2026-09-10T18:00",
        ],
        input="CommercialPassword123!\n",
    )

    assert result.exit_code == 1
    assert (
        "Event start must use ISO format YYYY-MM-DDTHH:MM."
        in result.stdout
    )


def test_cli_sentry_command_requires_management(
    commercial_user,
):
    """A commercial collaborator cannot trigger the Sentry test."""

    result = runner.invoke(
        app,
        [
            "monitoring",
            "test-sentry",
            commercial_user.email,
        ],
        input="CommercialPassword123!\n",
    )

    assert result.exit_code == 1
    assert "Permission denied." in result.stdout


def test_cli_sentry_command_reports_missing_configuration(
    management_user,
    monkeypatch,
):
    """The CLI explains when the Sentry DSN is missing."""

    monkeypatch.setattr(
        "src.cli.monitoring.initialize_sentry",
        lambda: False,
    )

    result = runner.invoke(
        app,
        [
            "monitoring",
            "test-sentry",
            management_user.email,
        ],
        input="ManagementPassword123!\n",
    )

    assert result.exit_code == 1
    assert "Sentry is not configured." in result.stdout


def test_cli_sentry_command_success(
    management_user,
    monkeypatch,
):
    """A management collaborator can send the controlled event."""

    monkeypatch.setattr(
        "src.cli.monitoring.initialize_sentry",
        lambda: True,
    )
    monkeypatch.setattr(
        "src.cli.monitoring.send_test_exception",
        lambda: "event-456",
    )

    result = runner.invoke(
        app,
        [
            "monitoring",
            "test-sentry",
            management_user.email,
        ],
        input="ManagementPassword123!\n",
    )

    assert result.exit_code == 0
    assert "Sentry test exception sent successfully." in result.stdout
    assert "event-456" in result.stdout
