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