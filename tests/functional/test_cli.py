"""
Functional tests for the Epic Events Typer command-line interface.
"""

from typer.testing import CliRunner

from src.main import app


runner = CliRunner()


def test_cli_help_displays_main_commands():
    """The CLI help exposes the main CRM workflows."""

    result = runner.invoke(
        app,
        [
            "--help",
        ],
    )

    assert result.exit_code == 0
    assert "initialize-database" in result.stdout
    assert "create-client-command" in result.stdout
    assert "create-contract-command" in result.stdout
    assert "create-event-command" in result.stdout
    assert "test-sentry-command" in result.stdout


def test_cli_authentication_success(
    management_user,
):
    """Valid credentials authenticate a collaborator through the CLI."""

    result = runner.invoke(
        app,
        [
            "authenticate-user-command",
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
            "authenticate-user-command",
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
            "list-clients-command",
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
            "create-client-command",
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
            "create-event-command",
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
            "test-sentry-command",
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
        "src.main.initialize_sentry",
        lambda: False,
    )

    result = runner.invoke(
        app,
        [
            "test-sentry-command",
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
        "src.main.initialize_sentry",
        lambda: True,
    )
    monkeypatch.setattr(
        "src.main.send_test_exception",
        lambda: "event-456",
    )

    result = runner.invoke(
        app,
        [
            "test-sentry-command",
            management_user.email,
        ],
        input="ManagementPassword123!\n",
    )

    assert result.exit_code == 0
    assert "Sentry test exception sent successfully." in result.stdout
    assert "event-456" in result.stdout
