"""
event_service.py

Role:
- Implement event business logic.
- Validate event data.
- Enforce event-management permissions.
- Interact with the Event model.

All event-related database operations are centralized in this module.
"""

from datetime import datetime
from typing import Optional

from src.auth import require_permission
from src.models.contract import Contract
from src.models.event import Event
from src.models.user import User


EVENT_READ_DEPARTMENTS = (
    "COMMERCIAL",
    "SUPPORT",
    "MANAGEMENT",
)


def _validate_event_text(
    value: str,
    field_name: str,
) -> str:
    """
    Normalize and validate a required event text field.

    Returns:
        The normalized text value.

    Raises:
        ValueError: If the value is empty.
    """

    normalized_value = value.strip()

    if not normalized_value:
        raise ValueError(
            f"{field_name} is required."
        )

    return normalized_value


def _validate_attendees(
    attendees: int,
) -> int:
    """
    Validate the expected number of attendees.

    Returns:
        The validated attendee count.

    Raises:
        ValueError: If the value is not a positive integer.
    """

    if isinstance(attendees, bool) or not isinstance(attendees, int):
        raise ValueError(
            "Attendees must be a positive integer."
        )

    if attendees <= 0:
        raise ValueError(
            "Attendees must be greater than zero."
        )

    return attendees


def _validate_event_dates(
    event_start: datetime,
    event_end: datetime,
) -> tuple[datetime, datetime]:
    """
    Validate event start and end dates.

    Returns:
        The validated start and end dates.

    Raises:
        ValueError: If a value is not a datetime or if the event does
        not end after it starts.
    """

    if not isinstance(event_start, datetime):
        raise ValueError(
            "Event start must be a valid datetime."
        )

    if not isinstance(event_end, datetime):
        raise ValueError(
            "Event end must be a valid datetime."
        )

    if event_end <= event_start:
        raise ValueError(
            "Event end must be after event start."
        )

    return event_start, event_end


def _normalize_notes(
    notes: Optional[str],
) -> Optional[str]:
    """
    Normalize optional event notes.

    Empty notes are stored as None.
    """

    if notes is None:
        return None

    normalized_notes = notes.strip()

    if not normalized_notes:
        return None

    return normalized_notes


def _get_contract_by_id(
    contract_id: int,
) -> Contract:
    """
    Retrieve a contract by identifier.

    Raises:
        ValueError: If no contract matches the identifier.
    """

    contract = Contract.get_or_none(
        Contract.id == contract_id
    )

    if contract is None:
        raise ValueError("Contract not found.")

    return contract


def _get_event_by_id(
    event_id: int,
) -> Event:
    """
    Retrieve an event by identifier.

    Raises:
        ValueError: If no event matches the identifier.
    """

    event = Event.get_or_none(
        Event.id == event_id
    )

    if event is None:
        raise ValueError("Event not found.")

    return event


def _get_user_by_id(
    user_id: int,
) -> User:
    """
    Retrieve a collaborator by identifier.

    Raises:
        ValueError: If no collaborator matches the identifier.
    """

    user = User.get_or_none(
        User.id == user_id
    )

    if user is None:
        raise ValueError("User not found.")

    return user


def create_event(
    contract_id: int,
    event_name: str,
    location: str,
    attendees: int,
    event_start: datetime,
    event_end: datetime,
    notes: Optional[str],
    current_user: User,
) -> Event:
    """
    Create a new event for a signed contract.

    Only an authenticated and active commercial collaborator may create
    an event. The commercial must be responsible for the client linked
    to the selected contract, and the contract must already be signed.

    Returns:
        The newly created event.

    Raises:
        PermissionError: If the current user is not authorized or does
        not own the related client.
        ValueError: If the contract does not exist, is unsigned or the
        event data is invalid.
    """

    require_permission(
        current_user,
        "COMMERCIAL",
    )

    contract = _get_contract_by_id(
        contract_id=contract_id,
    )

    if contract.client.sales_contact_id != current_user.id:
        raise PermissionError(
            "You can only create events for your own clients."
        )

    if not contract.is_signed:
        raise ValueError(
            "An event can only be created for a signed contract."
        )

    normalized_event_name = _validate_event_text(
        value=event_name,
        field_name="Event name",
    )

    normalized_location = _validate_event_text(
        value=location,
        field_name="Location",
    )

    validated_attendees = _validate_attendees(
        attendees=attendees,
    )

    validated_event_start, validated_event_end = (
        _validate_event_dates(
            event_start=event_start,
            event_end=event_end,
        )
    )

    normalized_notes = _normalize_notes(
        notes=notes,
    )

    return Event.create(
        contract=contract,
        support_contact=None,
        event_name=normalized_event_name,
        location=normalized_location,
        attendees=validated_attendees,
        event_start=validated_event_start,
        event_end=validated_event_end,
        notes=normalized_notes,
    )


def list_all_events(
    current_user: User,
) -> list[Event]:
    """
    Retrieve every event stored in the CRM.

    All authenticated and active collaborators may consult all events
    in read-only mode.

    Returns:
        A list of events ordered by start date and identifier.

    Raises:
        PermissionError: If the current user is not authorized.
    """

    require_permission(
        current_user,
        *EVENT_READ_DEPARTMENTS,
    )

    return list(
        Event.select().order_by(
            Event.event_start,
            Event.id,
        )
    )


def list_unassigned_events(
    current_user: User,
) -> list[Event]:
    """
    Retrieve events without an assigned support collaborator.

    This filter is available only to authenticated and active management
    collaborators.

    Returns:
        A list of unassigned events ordered by start date and identifier.

    Raises:
        PermissionError: If the current user is not authorized.
    """

    require_permission(
        current_user,
        "MANAGEMENT",
    )

    return list(
        Event.select()
        .where(Event.support_contact.is_null(True))
        .order_by(
            Event.event_start,
            Event.id,
        )
    )


def list_my_support_events(
    current_user: User,
) -> list[Event]:
    """
    Retrieve events assigned to the authenticated support collaborator.

    Returns:
        A list of assigned events ordered by start date and identifier.

    Raises:
        PermissionError: If the current user is not an active support
        collaborator.
    """

    require_permission(
        current_user,
        "SUPPORT",
    )

    return list(
        Event.select()
        .where(Event.support_contact == current_user)
        .order_by(
            Event.event_start,
            Event.id,
        )
    )


def assign_support_to_event(
    event_id: int,
    support_user_id: int,
    current_user: User,
) -> Event:
    """
    Assign an active support collaborator to an event.

    Only an authenticated and active management collaborator may perform
    this operation.

    Returns:
        The updated event.

    Raises:
        PermissionError: If the current user is not authorized.
        ValueError: If the event or collaborator does not exist, or the
        selected collaborator is not an active support user.
    """

    require_permission(
        current_user,
        "MANAGEMENT",
    )

    event = _get_event_by_id(
        event_id=event_id,
    )

    support_user = _get_user_by_id(
        user_id=support_user_id,
    )

    if (
        not support_user.is_active
        or support_user.department.strip().upper() != "SUPPORT"
    ):
        raise ValueError(
            "Selected user must be an active support collaborator."
        )

    event.support_contact = support_user

    event.save(
        only=[
            Event.support_contact,
        ]
    )

    return event


def update_event(
    event_id: int,
    event_name: str,
    location: str,
    attendees: int,
    event_start: datetime,
    event_end: datetime,
    notes: Optional[str],
    current_user: User,
) -> Event:
    """
    Update an event assigned to the authenticated support collaborator.

    Support collaborators may update only events for which they are the
    assigned support contact. Assignment itself remains a management
    responsibility.

    Returns:
        The updated event.

    Raises:
        PermissionError: If the current user is not an active support
        collaborator or is not assigned to the selected event.
        ValueError: If the event does not exist or the event data is
        invalid.
    """

    require_permission(
        current_user,
        "SUPPORT",
    )

    event = _get_event_by_id(
        event_id=event_id,
    )

    if event.support_contact_id != current_user.id:
        raise PermissionError(
            "You can only update events assigned to you."
        )

    normalized_event_name = _validate_event_text(
        value=event_name,
        field_name="Event name",
    )

    normalized_location = _validate_event_text(
        value=location,
        field_name="Location",
    )

    validated_attendees = _validate_attendees(
        attendees=attendees,
    )

    validated_event_start, validated_event_end = (
        _validate_event_dates(
            event_start=event_start,
            event_end=event_end,
        )
    )

    normalized_notes = _normalize_notes(
        notes=notes,
    )

    event.event_name = normalized_event_name
    event.location = normalized_location
    event.attendees = validated_attendees
    event.event_start = validated_event_start
    event.event_end = validated_event_end
    event.notes = normalized_notes

    event.save(
        only=[
            Event.event_name,
            Event.location,
            Event.attendees,
            Event.event_start,
            Event.event_end,
            Event.notes,
        ]
    )

    return event
