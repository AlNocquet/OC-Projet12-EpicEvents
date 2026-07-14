"""
Tests for the event service layer.
"""

from datetime import datetime, timedelta

import pytest

from src.models.event import Event
from src.services.client_service import create_client
from src.services.contract_service import create_contract
from src.services.event_service import (
    assign_support_to_event,
    create_event,
    list_all_events,
    list_my_support_events,
    list_unassigned_events,
    update_event,
)


EVENT_START = datetime(2026, 9, 10, 9, 0)
EVENT_END = datetime(2026, 9, 10, 18, 0)


def test_create_event_success(
    commercial_user,
    signed_contract,
):
    """
    Happy Path

    A commercial collaborator creates an event for their own client
    after the related contract has been signed.
    """

    event = create_event(
        contract_id=signed_contract.id,
        event_name="  Annual Conference  ",
        location="  Paris Expo  ",
        attendees=250,
        event_start=EVENT_START,
        event_end=EVENT_END,
        notes="  Prepare the registration desk.  ",
        current_user=commercial_user,
    )

    assert event.contract_id == signed_contract.id
    assert event.support_contact_id is None
    assert event.event_name == "Annual Conference"
    assert event.location == "Paris Expo"
    assert event.attendees == 250
    assert event.event_start == EVENT_START
    assert event.event_end == EVENT_END
    assert event.notes == "Prepare the registration desk."
    assert Event.select().count() == 1


def test_create_event_with_empty_notes_stores_none(
    commercial_user,
    signed_contract,
):
    """
    Happy Path

    Empty optional notes are stored as None.
    """

    event = create_event(
        contract_id=signed_contract.id,
        event_name="Annual Conference",
        location="Paris Expo",
        attendees=250,
        event_start=EVENT_START,
        event_end=EVENT_END,
        notes="   ",
        current_user=commercial_user,
    )

    assert event.notes is None


def test_create_event_without_commercial_permission(
    management_user,
    signed_contract,
):
    """
    Sad Path

    A management collaborator cannot create an event.
    """

    with pytest.raises(
        PermissionError,
        match="Permission denied.",
    ):
        create_event(
            contract_id=signed_contract.id,
            event_name="Annual Conference",
            location="Paris Expo",
            attendees=250,
            event_start=EVENT_START,
            event_end=EVENT_END,
            notes=None,
            current_user=management_user,
        )


def test_create_event_with_support_user(
    support_user,
    signed_contract,
):
    """
    Sad Path

    A support collaborator cannot create an event.
    """

    with pytest.raises(
        PermissionError,
        match="Permission denied.",
    ):
        create_event(
            contract_id=signed_contract.id,
            event_name="Annual Conference",
            location="Paris Expo",
            attendees=250,
            event_start=EVENT_START,
            event_end=EVENT_END,
            notes=None,
            current_user=support_user,
        )


def test_create_event_without_authenticated_user(
    signed_contract,
):
    """
    Sad Path

    An unauthenticated user cannot create an event.
    """

    with pytest.raises(
        PermissionError,
        match="Permission denied.",
    ):
        create_event(
            contract_id=signed_contract.id,
            event_name="Annual Conference",
            location="Paris Expo",
            attendees=250,
            event_start=EVENT_START,
            event_end=EVENT_END,
            notes=None,
            current_user=None,
        )


def test_create_event_with_inactive_commercial_user(
    commercial_user,
    signed_contract,
):
    """
    Sad Path

    An inactive commercial collaborator cannot create an event.
    """

    commercial_user.is_active = False
    commercial_user.save()

    with pytest.raises(
        PermissionError,
        match="Permission denied.",
    ):
        create_event(
            contract_id=signed_contract.id,
            event_name="Annual Conference",
            location="Paris Expo",
            attendees=250,
            event_start=EVENT_START,
            event_end=EVENT_END,
            notes=None,
            current_user=commercial_user,
        )


def test_create_event_with_unknown_contract(
    commercial_user,
):
    """
    Sad Path

    Creating an event for an unknown contract raises an error.
    """

    with pytest.raises(
        ValueError,
        match="Contract not found.",
    ):
        create_event(
            contract_id=9999,
            event_name="Annual Conference",
            location="Paris Expo",
            attendees=250,
            event_start=EVENT_START,
            event_end=EVENT_END,
            notes=None,
            current_user=commercial_user,
        )


def test_create_event_for_unsigned_contract(
    commercial_user,
    contract,
):
    """
    Sad Path

    An event cannot be created before the contract is signed.
    """

    with pytest.raises(
        ValueError,
        match="An event can only be created for a signed contract.",
    ):
        create_event(
            contract_id=contract.id,
            event_name="Annual Conference",
            location="Paris Expo",
            attendees=250,
            event_start=EVENT_START,
            event_end=EVENT_END,
            notes=None,
            current_user=commercial_user,
        )


def test_create_event_for_another_commercial_client(
    management_user,
    second_commercial_user,
    signed_contract,
):
    """
    Sad Path

    A commercial collaborator cannot create an event for another
    commercial collaborator's client.
    """

    with pytest.raises(
        PermissionError,
        match="You can only create events for your own clients.",
    ):
        create_event(
            contract_id=signed_contract.id,
            event_name="Annual Conference",
            location="Paris Expo",
            attendees=250,
            event_start=EVENT_START,
            event_end=EVENT_END,
            notes=None,
            current_user=second_commercial_user,
        )


def test_create_event_with_empty_event_name(
    commercial_user,
    signed_contract,
):
    """
    Sad Path

    An event name is required.
    """

    with pytest.raises(
        ValueError,
        match="Event name is required.",
    ):
        create_event(
            contract_id=signed_contract.id,
            event_name="",
            location="Paris Expo",
            attendees=250,
            event_start=EVENT_START,
            event_end=EVENT_END,
            notes=None,
            current_user=commercial_user,
        )


def test_create_event_with_empty_location(
    commercial_user,
    signed_contract,
):
    """
    Sad Path

    An event location is required.
    """

    with pytest.raises(
        ValueError,
        match="Location is required.",
    ):
        create_event(
            contract_id=signed_contract.id,
            event_name="Annual Conference",
            location="",
            attendees=250,
            event_start=EVENT_START,
            event_end=EVENT_END,
            notes=None,
            current_user=commercial_user,
        )


@pytest.mark.parametrize(
    "attendees, expected_message",
    [
        (0, "Attendees must be greater than zero."),
        (-1, "Attendees must be greater than zero."),
        (True, "Attendees must be a positive integer."),
        ("250", "Attendees must be a positive integer."),
    ],
)
def test_create_event_with_invalid_attendees(
    commercial_user,
    signed_contract,
    attendees,
    expected_message,
):
    """
    Sad Path

    The attendee count must be a positive integer.
    """

    with pytest.raises(
        ValueError,
        match=expected_message,
    ):
        create_event(
            contract_id=signed_contract.id,
            event_name="Annual Conference",
            location="Paris Expo",
            attendees=attendees,
            event_start=EVENT_START,
            event_end=EVENT_END,
            notes=None,
            current_user=commercial_user,
        )


@pytest.mark.parametrize(
    "event_end",
    [
        EVENT_START,
        EVENT_START - timedelta(minutes=1),
    ],
)
def test_create_event_with_invalid_date_order(
    commercial_user,
    signed_contract,
    event_end,
):
    """
    Sad Path

    The event must end after it starts.
    """

    with pytest.raises(
        ValueError,
        match="Event end must be after event start.",
    ):
        create_event(
            contract_id=signed_contract.id,
            event_name="Annual Conference",
            location="Paris Expo",
            attendees=250,
            event_start=EVENT_START,
            event_end=event_end,
            notes=None,
            current_user=commercial_user,
        )


def test_list_all_events_returns_empty_list(
    commercial_user,
):
    """
    Happy Path

    Event consultation returns an empty list when no event exists.
    """

    assert list_all_events(
        current_user=commercial_user,
    ) == []


def test_list_all_events_is_available_to_every_department(
    commercial_user,
    management_user,
    support_user,
    unassigned_event,
):
    """
    Happy Path

    Commercial, management and support collaborators can consult all
    events in read-only mode.
    """

    for current_user in (
        commercial_user,
        management_user,
        support_user,
    ):
        events = list_all_events(
            current_user=current_user,
        )

        assert [
            event.id
            for event in events
        ] == [unassigned_event.id]


def test_list_all_events_without_authenticated_user(
    test_database,
):
    """
    Sad Path

    An unauthenticated user cannot consult events.
    """

    with pytest.raises(
        PermissionError,
        match="Permission denied.",
    ):
        list_all_events(
            current_user=None,
        )


def test_list_unassigned_events_success(
    management_user,
    unassigned_event,
):
    """
    Happy Path

    Management collaborators can filter events without support.
    """

    events = list_unassigned_events(
        current_user=management_user,
    )

    assert [event.id for event in events] == [unassigned_event.id]


def test_list_unassigned_events_excludes_assigned_events(
    management_user,
    assigned_event,
):
    """
    Happy Path

    Assigned events are excluded from the management filter.
    """

    assert list_unassigned_events(
        current_user=management_user,
    ) == []


def test_list_unassigned_events_without_management_permission(
    commercial_user,
    unassigned_event,
):
    """
    Sad Path

    Commercial collaborators cannot use the management filter.
    """

    with pytest.raises(
        PermissionError,
        match="Permission denied.",
    ):
        list_unassigned_events(
            current_user=commercial_user,
        )


def test_list_my_support_events_success(
    support_user,
    assigned_event,
):
    """
    Happy Path

    A support collaborator can filter events assigned to them.
    """

    events = list_my_support_events(
        current_user=support_user,
    )

    assert [event.id for event in events] == [assigned_event.id]


def test_list_my_support_events_excludes_other_support_assignments(
    management_user,
    support_user,
    second_support_user,
    unassigned_event,
):
    """
    Happy Path

    A support collaborator sees only their own assigned events.
    """

    assign_support_to_event(
        event_id=unassigned_event.id,
        support_user_id=second_support_user.id,
        current_user=management_user,
    )

    assert list_my_support_events(
        current_user=support_user,
    ) == []


def test_list_my_support_events_without_support_permission(
    management_user,
    unassigned_event,
):
    """
    Sad Path

    Management collaborators cannot use the personal support filter.
    """

    with pytest.raises(
        PermissionError,
        match="Permission denied.",
    ):
        list_my_support_events(
            current_user=management_user,
        )


def test_assign_support_to_event_success(
    management_user,
    support_user,
    unassigned_event,
):
    """
    Happy Path

    Management assigns an active support collaborator to an event.
    """

    event = assign_support_to_event(
        event_id=unassigned_event.id,
        support_user_id=support_user.id,
        current_user=management_user,
    )

    stored_event = Event.get_by_id(
        unassigned_event.id
    )

    assert event.support_contact_id == support_user.id
    assert stored_event.support_contact_id == support_user.id


def test_assign_support_without_management_permission_checks_role_first(
    commercial_user,
):
    """
    Sad Path

    An unauthorized collaborator is rejected before event lookup.
    """

    with pytest.raises(
        PermissionError,
        match="Permission denied.",
    ):
        assign_support_to_event(
            event_id=9999,
            support_user_id=9999,
            current_user=commercial_user,
        )


def test_assign_support_to_unknown_event(
    management_user,
    support_user,
):
    """
    Sad Path

    Assigning support to an unknown event raises an error.
    """

    with pytest.raises(
        ValueError,
        match="Event not found.",
    ):
        assign_support_to_event(
            event_id=9999,
            support_user_id=support_user.id,
            current_user=management_user,
        )


def test_assign_unknown_support_user(
    management_user,
    unassigned_event,
):
    """
    Sad Path

    Assigning an unknown collaborator raises an error.
    """

    with pytest.raises(
        ValueError,
        match="User not found.",
    ):
        assign_support_to_event(
            event_id=unassigned_event.id,
            support_user_id=9999,
            current_user=management_user,
        )


def test_assign_non_support_user(
    management_user,
    commercial_user,
    unassigned_event,
):
    """
    Sad Path

    Only a support collaborator can be assigned to an event.
    """

    with pytest.raises(
        ValueError,
        match="Selected user must be an active support collaborator.",
    ):
        assign_support_to_event(
            event_id=unassigned_event.id,
            support_user_id=commercial_user.id,
            current_user=management_user,
        )


def test_assign_inactive_support_user(
    management_user,
    support_user,
    unassigned_event,
):
    """
    Sad Path

    An inactive support collaborator cannot be assigned to an event.
    """

    support_user.is_active = False
    support_user.save()

    with pytest.raises(
        ValueError,
        match="Selected user must be an active support collaborator.",
    ):
        assign_support_to_event(
            event_id=unassigned_event.id,
            support_user_id=support_user.id,
            current_user=management_user,
        )


def test_update_assigned_event_success(
    support_user,
    assigned_event,
):
    """
    Happy Path

    A support collaborator updates an event assigned to them.
    """

    updated_start = EVENT_START + timedelta(days=1)
    updated_end = EVENT_END + timedelta(days=1)

    event = update_event(
        event_id=assigned_event.id,
        event_name="  Updated Conference  ",
        location="  Lyon Convention Center  ",
        attendees=300,
        event_start=updated_start,
        event_end=updated_end,
        notes="  Updated logistics.  ",
        current_user=support_user,
    )

    stored_event = Event.get_by_id(
        assigned_event.id
    )

    assert event.event_name == "Updated Conference"
    assert stored_event.location == "Lyon Convention Center"
    assert stored_event.attendees == 300
    assert stored_event.event_start == updated_start
    assert stored_event.event_end == updated_end
    assert stored_event.notes == "Updated logistics."
    assert stored_event.support_contact_id == support_user.id


def test_update_unassigned_event(
    support_user,
    unassigned_event,
):
    """
    Sad Path

    A support collaborator cannot update an unassigned event.
    """

    with pytest.raises(
        PermissionError,
        match="You can only update events assigned to you.",
    ):
        update_event(
            event_id=unassigned_event.id,
            event_name=unassigned_event.event_name,
            location=unassigned_event.location,
            attendees=unassigned_event.attendees,
            event_start=unassigned_event.event_start,
            event_end=unassigned_event.event_end,
            notes=unassigned_event.notes,
            current_user=support_user,
        )


def test_update_event_assigned_to_another_support(
    second_support_user,
    assigned_event,
):
    """
    Sad Path

    A support collaborator cannot update another support user's event.
    """

    with pytest.raises(
        PermissionError,
        match="You can only update events assigned to you.",
    ):
        update_event(
            event_id=assigned_event.id,
            event_name=assigned_event.event_name,
            location=assigned_event.location,
            attendees=assigned_event.attendees,
            event_start=assigned_event.event_start,
            event_end=assigned_event.event_end,
            notes=assigned_event.notes,
            current_user=second_support_user,
        )


def test_update_event_without_support_permission_checks_role_first(
    management_user,
):
    """
    Sad Path

    An unauthorized collaborator is rejected before event lookup.
    """

    with pytest.raises(
        PermissionError,
        match="Permission denied.",
    ):
        update_event(
            event_id=9999,
            event_name="Unknown Event",
            location="Unknown Location",
            attendees=1,
            event_start=EVENT_START,
            event_end=EVENT_END,
            notes=None,
            current_user=management_user,
        )


def test_update_unknown_event(
    support_user,
):
    """
    Sad Path

    An active support collaborator receives an explicit error for an
    unknown event.
    """

    with pytest.raises(
        ValueError,
        match="Event not found.",
    ):
        update_event(
            event_id=9999,
            event_name="Unknown Event",
            location="Unknown Location",
            attendees=1,
            event_start=EVENT_START,
            event_end=EVENT_END,
            notes=None,
            current_user=support_user,
        )


def test_update_event_with_invalid_data(
    support_user,
    assigned_event,
):
    """
    Sad Path

    Event validation rules also apply during updates.
    """

    with pytest.raises(
        ValueError,
        match="Attendees must be greater than zero.",
    ):
        update_event(
            event_id=assigned_event.id,
            event_name=assigned_event.event_name,
            location=assigned_event.location,
            attendees=0,
            event_start=assigned_event.event_start,
            event_end=assigned_event.event_end,
            notes=assigned_event.notes,
            current_user=support_user,
        )
