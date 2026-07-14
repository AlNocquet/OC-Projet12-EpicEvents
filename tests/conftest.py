"""
conftest.py

Shared pytest fixtures for the Epic Events test suite.
"""

import pytest

from src.database import database

from src.models.client import Client
from src.models.contract import Contract
from src.models.event import Event
from src.models.user import User

from src.services.client_service import create_client
from src.services.contract_service import create_contract
from src.services.event_service import (
    assign_support_to_event,
    create_event,
)
from src.services.user_service import (
    create_initial_management_user,
    create_user,
)


@pytest.fixture(scope="function")
def test_database():
    """
    Prepare a clean database for each test.

    Creates every CRM table before the test and removes them
    afterwards to guarantee test isolation.
    """

    database.connect(reuse_if_open=True)

    database.drop_tables(
        [
            Event,
            Contract,
            Client,
            User,
        ],
        safe=True,
    )

    database.create_tables(
        [
            User,
            Client,
            Contract,
            Event,
        ],
        safe=True,
    )

    yield database

    database.drop_tables(
        [
            Event,
            Contract,
            Client,
            User,
        ],
        safe=True,
    )

    if not database.is_closed():
        database.close()


@pytest.fixture
def management_user(test_database):
    """
    Create an active management user.
    """

    return create_initial_management_user(
        full_name="Morgan Manager",
        email="manager@epicevents.com",
        password="ManagementPassword123!",
    )


@pytest.fixture
def commercial_user(
    management_user,
):
    """
    Create an active commercial user.
    """

    return create_user(
        full_name="Casey Commercial",
        email="commercial@epicevents.com",
        password="CommercialPassword123!",
        department="COMMERCIAL",
        current_user=management_user,
    )


@pytest.fixture
def second_commercial_user(
    management_user,
):
    """
    Create a second active commercial user.
    """

    return create_user(
        full_name="Taylor Commercial",
        email="second.commercial@epicevents.com",
        password="SecondCommercialPassword123!",
        department="COMMERCIAL",
        current_user=management_user,
    )


@pytest.fixture
def support_user(
    management_user,
):
    """
    Create an active support user.
    """

    return create_user(
        full_name="Sam Support",
        email="support@epicevents.com",
        password="SupportPassword123!",
        department="SUPPORT",
        current_user=management_user,
    )


@pytest.fixture
def client(
    commercial_user,
):
    """
    Create a client assigned to the primary commercial user.
    """

    return create_client(
        full_name="Kevin Casey",
        email="kevin@startup.io",
        phone="+678 123 456 78",
        company_name="Cool Startup LLC",
        current_user=commercial_user,
    )


@pytest.fixture
def contract(
    management_user,
    client,
):
    """
    Create an unsigned and partially unpaid contract.
    """

    return create_contract(
        client_id=client.id,
        total_amount="10000.00",
        amount_due="2500.00",
        is_signed=False,
        current_user=management_user,
    )

@pytest.fixture
def second_support_user(
    management_user,
):
    """
    Create a second active support user.
    """

    return create_user(
        full_name="Jordan Support",
        email="second.support@epicevents.com",
        password="SecondSupportPassword123!",
        department="SUPPORT",
        current_user=management_user,
    )


@pytest.fixture
def signed_contract(
    management_user,
    client,
):
    """
    Create a signed contract for the primary commercial user's client.
    """

    return create_contract(
        client_id=client.id,
        total_amount="15000.00",
        amount_due="5000.00",
        is_signed=True,
        current_user=management_user,
    )


@pytest.fixture
def unassigned_event(
    commercial_user,
    signed_contract,
):
    """
    Create an event without an assigned support collaborator.
    """

    from datetime import datetime

    return create_event(
        contract_id=signed_contract.id,
        event_name="Product Launch",
        location="Paris Convention Center",
        attendees=120,
        event_start=datetime(2026, 8, 20, 9, 0),
        event_end=datetime(2026, 8, 20, 18, 0),
        notes="Prepare the main conference room.",
        current_user=commercial_user,
    )


@pytest.fixture
def assigned_event(
    management_user,
    support_user,
    unassigned_event,
):
    """
    Create an event assigned to the primary support user.
    """

    return assign_support_to_event(
        event_id=unassigned_event.id,
        support_user_id=support_user.id,
        current_user=management_user,
    )

