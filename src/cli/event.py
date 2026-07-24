"""
CLI commands used to manage CRM events.
"""

from datetime import datetime

import typer

from src.cli.common import authenticate_current_user
from src.models.event import Event
from src.services.event_service import (
    assign_support_to_event as assign_support_to_event_service,
    create_event as create_event_service,
    list_all_events as list_all_events_service,
    list_my_support_events as list_my_support_events_service,
    list_unassigned_events as list_unassigned_events_service,
    update_event as update_event_service,
)


app = typer.Typer(
    help="Manage CRM events.",
    no_args_is_help=True,
)


def _parse_datetime(
    value: str,
    field_name: str,
) -> datetime:
    """
    Parse an ISO-formatted datetime supplied through the CLI.

    Accepted examples include ``2026-07-20T14:30`` and
    ``2026-07-20 14:30``.
    """

    try:
        return datetime.fromisoformat(
            value.strip(),
        )

    except (TypeError, ValueError) as error:
        raise ValueError(
            f"{field_name} must use ISO format "
            "YYYY-MM-DDTHH:MM."
        ) from error


def _display_events(
    events: list[Event],
) -> None:
    """Display a collection of events in the terminal."""

    if not events:
        typer.echo("No events found.")
        return

    for event in events:
        support_name = (
            event.support_contact.full_name
            if event.support_contact_id is not None
            else "Unassigned"
        )

        typer.echo(
            f"ID: {event.id} | "
            f"Event: {event.event_name} | "
            f"Contract: {event.contract.id} | "
            f"Client: {event.contract.client.full_name} | "
            f"Support: {support_name} | "
            f"Location: {event.location} | "
            f"Attendees: {event.attendees} | "
            f"Start: {event.event_start:%Y-%m-%d %H:%M} | "
            f"End: {event.event_end:%Y-%m-%d %H:%M} | "
            f"Notes: {event.notes or '-'}"
        )


@app.command("create")
def create(
    authenticated_email: str,
    contract_id: int,
    event_name: str,
    location: str,
    attendees: int,
    event_start: str,
    event_end: str,
    notes: str = "",
) -> None:
    """
    Create an event for a signed contract.

    Only the authenticated commercial collaborator responsible for the
    related client may create the event. Datetimes must use ISO format.
    """

    current_user = authenticate_current_user(
        email=authenticated_email,
    )

    try:
        parsed_event_start = _parse_datetime(
            value=event_start,
            field_name="Event start",
        )
        parsed_event_end = _parse_datetime(
            value=event_end,
            field_name="Event end",
        )

        event = create_event_service(
            contract_id=contract_id,
            event_name=event_name,
            location=location,
            attendees=attendees,
            event_start=parsed_event_start,
            event_end=parsed_event_end,
            notes=notes,
            current_user=current_user,
        )

        typer.echo(
            "Event created successfully. "
            f"Event ID: {event.id}."
        )

    except (ValueError, PermissionError) as error:
        typer.echo(str(error))
        raise typer.Exit(code=1) from error


@app.command("list")
def list_events(
    authenticated_email: str,
) -> None:
    """
    Display every event stored in the CRM.

    All authenticated and active collaborators may consult events in
    read-only mode.
    """

    current_user = authenticate_current_user(
        email=authenticated_email,
    )

    try:
        events = list_all_events_service(
            current_user=current_user,
        )

    except PermissionError as error:
        typer.echo(str(error))
        raise typer.Exit(code=1) from error

    _display_events(
        events=events,
    )


@app.command("list-unassigned")
def list_unassigned(
    authenticated_email: str,
) -> None:
    """
    Display events without an assigned support collaborator.

    This filter is available only to authenticated and active management
    collaborators.
    """

    current_user = authenticate_current_user(
        email=authenticated_email,
    )

    try:
        events = list_unassigned_events_service(
            current_user=current_user,
        )

    except PermissionError as error:
        typer.echo(str(error))
        raise typer.Exit(code=1) from error

    _display_events(
        events=events,
    )


@app.command("list-mine")
def list_mine(
    authenticated_email: str,
) -> None:
    """
    Display events assigned to the authenticated support collaborator.
    """

    current_user = authenticate_current_user(
        email=authenticated_email,
    )

    try:
        events = list_my_support_events_service(
            current_user=current_user,
        )

    except PermissionError as error:
        typer.echo(str(error))
        raise typer.Exit(code=1) from error

    _display_events(
        events=events,
    )


@app.command("assign-support")
def assign_support(
    authenticated_email: str,
    event_id: int,
    support_user_id: int,
) -> None:
    """
    Assign an active support collaborator to an event.

    Only an authenticated and active management collaborator may assign
    the support contact.
    """

    current_user = authenticate_current_user(
        email=authenticated_email,
    )

    try:
        event = assign_support_to_event_service(
            event_id=event_id,
            support_user_id=support_user_id,
            current_user=current_user,
        )

        typer.echo(
            f"Support collaborator assigned to event {event.id}."
        )

    except (ValueError, PermissionError) as error:
        typer.echo(str(error))
        raise typer.Exit(code=1) from error


@app.command("update")
def update(
    authenticated_email: str,
    event_id: int,
    event_name: str,
    location: str,
    attendees: int,
    event_start: str,
    event_end: str,
    notes: str = "",
) -> None:
    """
    Update an event assigned to the authenticated support collaborator.

    Datetimes must use ISO format.
    """

    current_user = authenticate_current_user(
        email=authenticated_email,
    )

    try:
        parsed_event_start = _parse_datetime(
            value=event_start,
            field_name="Event start",
        )
        parsed_event_end = _parse_datetime(
            value=event_end,
            field_name="Event end",
        )

        event = update_event_service(
            event_id=event_id,
            event_name=event_name,
            location=location,
            attendees=attendees,
            event_start=parsed_event_start,
            event_end=parsed_event_end,
            notes=notes,
            current_user=current_user,
        )

        typer.echo(
            f"Event {event.id} updated successfully."
        )

    except (ValueError, PermissionError) as error:
        typer.echo(str(error))
        raise typer.Exit(code=1) from error