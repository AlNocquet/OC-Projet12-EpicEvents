"""
test_client_service.py

Tests for the client service layer.
"""

from datetime import datetime

import pytest

from src.models.client import Client

from src.services.client_service import (
    create_client,
    list_all_clients,
    update_client,
)


def test_create_client_success(
    commercial_user,
):
    """
    Happy Path

    A commercial collaborator creates a client who is automatically
    assigned to them.
    """

    client = create_client(
        full_name="  Kevin Casey  ",
        email="  KEVIN@STARTUP.IO  ",
        phone="  +678 123 456 78  ",
        company_name="  Cool Startup LLC  ",
        current_user=commercial_user,
    )

    assert client.full_name == "Kevin Casey"
    assert client.email == "kevin@startup.io"
    assert client.phone == "+678 123 456 78"
    assert client.company_name == "Cool Startup LLC"
    assert client.sales_contact_id == commercial_user.id
    assert client.created_at is not None
    assert client.updated_at is not None
    assert Client.select().count() == 1


def test_create_client_without_commercial_permission(
    management_user,
):
    """
    Sad Path

    A management collaborator cannot create a client.
    """

    with pytest.raises(
        PermissionError,
        match="Permission denied.",
    ):
        create_client(
            full_name="Kevin Casey",
            email="kevin@startup.io",
            phone="+678 123 456 78",
            company_name="Cool Startup LLC",
            current_user=management_user,
        )


def test_create_client_with_support_user(
    support_user,
):
    """
    Sad Path

    A support collaborator cannot create a client.
    """

    with pytest.raises(
        PermissionError,
        match="Permission denied.",
    ):
        create_client(
            full_name="Kevin Casey",
            email="kevin@startup.io",
            phone="+678 123 456 78",
            company_name="Cool Startup LLC",
            current_user=support_user,
        )


def test_create_client_with_inactive_commercial_user(
    commercial_user,
):
    """
    Sad Path

    An inactive commercial collaborator cannot create a client.
    """

    commercial_user.is_active = False
    commercial_user.save()

    with pytest.raises(
        PermissionError,
        match="Permission denied.",
    ):
        create_client(
            full_name="Kevin Casey",
            email="kevin@startup.io",
            phone="+678 123 456 78",
            company_name="Cool Startup LLC",
            current_user=commercial_user,
        )


def test_create_client_with_empty_full_name(
    commercial_user,
):
    """
    Sad Path

    Creating a client without a full name raises an error.
    """

    with pytest.raises(
        ValueError,
        match="Full name is required.",
    ):
        create_client(
            full_name="",
            email="kevin@startup.io",
            phone="+678 123 456 78",
            company_name="Cool Startup LLC",
            current_user=commercial_user,
        )


def test_create_client_with_empty_email(
    commercial_user,
):
    """
    Sad Path

    Creating a client without an email raises an error.
    """

    with pytest.raises(
        ValueError,
        match="Email is required.",
    ):
        create_client(
            full_name="Kevin Casey",
            email="",
            phone="+678 123 456 78",
            company_name="Cool Startup LLC",
            current_user=commercial_user,
        )


def test_create_client_with_empty_phone(
    commercial_user,
):
    """
    Sad Path

    Creating a client without a phone number raises an error.
    """

    with pytest.raises(
        ValueError,
        match="Phone number is required.",
    ):
        create_client(
            full_name="Kevin Casey",
            email="kevin@startup.io",
            phone="",
            company_name="Cool Startup LLC",
            current_user=commercial_user,
        )


def test_create_client_with_empty_company_name(
    commercial_user,
):
    """
    Sad Path

    Creating a client without a company name raises an error.
    """

    with pytest.raises(
        ValueError,
        match="Company name is required.",
    ):
        create_client(
            full_name="Kevin Casey",
            email="kevin@startup.io",
            phone="+678 123 456 78",
            company_name="",
            current_user=commercial_user,
        )


def test_create_client_with_existing_email(
    commercial_user,
    client,
):
    """
    Sad Path

    Two clients cannot share the same normalized email address.
    """

    with pytest.raises(
        ValueError,
        match="A client with this email already exists.",
    ):
        create_client(
            full_name="Another Client",
            email="KEVIN@STARTUP.IO",
            phone="+33 1 23 45 67 89",
            company_name="Another Company",
            current_user=commercial_user,
        )


def test_list_all_clients_returns_empty_list(
    commercial_user,
):
    """
    Happy Path

    Client consultation returns an empty list when no client exists.
    """

    clients = list_all_clients(
        current_user=commercial_user,
    )

    assert clients == []


def test_list_all_clients_is_available_to_every_department(
    commercial_user,
    management_user,
    support_user,
    client,
):
    """
    Happy Path

    Commercial, management and support collaborators can consult all
    clients in read-only mode.
    """

    cool_startup_client = create_client(
        full_name="Alice Bernard",
        email="alice@coolstartup.io",
        phone="+33 1 11 22 33 44",
        company_name="Cool Startup LLC",
        current_user=commercial_user,
    )

    alpha_client = create_client(
        full_name="Zoé Martin",
        email="zoe@alphaevents.io",
        phone="+33 1 55 66 77 88",
        company_name="Alpha Events",
        current_user=commercial_user,
    )

    expected_ids = [
        alpha_client.id,
        cool_startup_client.id,
        client.id,
    ]

    for current_user in (
        commercial_user,
        management_user,
        support_user,
    ):
        clients = list_all_clients(
            current_user=current_user,
        )

        assert [
            stored_client.id
            for stored_client in clients
        ] == expected_ids


def test_list_all_clients_without_authenticated_user(
    test_database,
):
    """
    Sad Path

    An unauthenticated user cannot consult client information.
    """

    with pytest.raises(
        PermissionError,
        match="Permission denied.",
    ):
        list_all_clients(
            current_user=None,
        )


def test_list_all_clients_with_inactive_user(
    support_user,
):
    """
    Sad Path

    An inactive collaborator cannot consult client information.
    """

    support_user.is_active = False
    support_user.save()

    with pytest.raises(
        PermissionError,
        match="Permission denied.",
    ):
        list_all_clients(
            current_user=support_user,
        )


def test_update_own_client_success(
    commercial_user,
    client,
):
    """
    Happy Path

    A commercial collaborator updates a client assigned to them.
    """

    previous_update = datetime(
        2020,
        1,
        1,
    )

    client.updated_at = previous_update
    client.save(
        only=[
            Client.updated_at,
        ]
    )

    updated_client = update_client(
        client_id=client.id,
        full_name="  Kevin Updated  ",
        email="  UPDATED@STARTUP.IO  ",
        phone="  +33 1 98 76 54 32  ",
        company_name="  Updated Startup LLC  ",
        current_user=commercial_user,
    )

    stored_client = Client.get_by_id(
        client.id
    )

    assert updated_client.id == client.id
    assert stored_client.full_name == "Kevin Updated"
    assert stored_client.email == "updated@startup.io"
    assert stored_client.phone == "+33 1 98 76 54 32"
    assert stored_client.company_name == "Updated Startup LLC"
    assert stored_client.sales_contact_id == commercial_user.id
    assert stored_client.updated_at > previous_update


def test_update_client_with_same_email(
    commercial_user,
    client,
):
    """
    Happy Path

    A client can keep their existing email address during an update.
    """

    updated_client = update_client(
        client_id=client.id,
        full_name="Kevin Updated",
        email=client.email,
        phone=client.phone,
        company_name=client.company_name,
        current_user=commercial_user,
    )

    assert updated_client.email == "kevin@startup.io"
    assert updated_client.full_name == "Kevin Updated"


def test_update_unknown_client(
    commercial_user,
):
    """
    Sad Path

    Updating an unknown client raises an error.
    """

    with pytest.raises(
        ValueError,
        match="Client not found.",
    ):
        update_client(
            client_id=9999,
            full_name="Unknown Client",
            email="unknown@startup.io",
            phone="+33 1 23 45 67 89",
            company_name="Unknown Company",
            current_user=commercial_user,
        )


def test_update_client_assigned_to_another_commercial(
    client,
    second_commercial_user,
):
    """
    Sad Path

    A commercial collaborator cannot update another commercial's
    client.
    """

    with pytest.raises(
        PermissionError,
        match="You can only update your own clients.",
    ):
        update_client(
            client_id=client.id,
            full_name=client.full_name,
            email=client.email,
            phone=client.phone,
            company_name=client.company_name,
            current_user=second_commercial_user,
        )


def test_update_client_without_commercial_permission(
    management_user,
    client,
):
    """
    Sad Path

    A management collaborator cannot update a client.
    """

    with pytest.raises(
        PermissionError,
        match="Permission denied.",
    ):
        update_client(
            client_id=client.id,
            full_name=client.full_name,
            email=client.email,
            phone=client.phone,
            company_name=client.company_name,
            current_user=management_user,
        )


def test_update_client_with_existing_email(
    commercial_user,
    client,
):
    """
    Sad Path

    A client cannot receive another client's email address.
    """

    other_client = create_client(
        full_name="Alice Bernard",
        email="alice@startup.io",
        phone="+33 1 11 22 33 44",
        company_name="Another Startup",
        current_user=commercial_user,
    )

    with pytest.raises(
        ValueError,
        match="A client with this email already exists.",
    ):
        update_client(
            client_id=client.id,
            full_name=client.full_name,
            email=other_client.email,
            phone=client.phone,
            company_name=client.company_name,
            current_user=commercial_user,
        )


def test_update_client_with_empty_phone(
    commercial_user,
    client,
):
    """
    Sad Path

    Updating a client with an empty required field raises an error.
    """

    with pytest.raises(
        ValueError,
        match="Phone number is required.",
    ):
        update_client(
            client_id=client.id,
            full_name=client.full_name,
            email=client.email,
            phone="",
            company_name=client.company_name,
            current_user=commercial_user,
        )