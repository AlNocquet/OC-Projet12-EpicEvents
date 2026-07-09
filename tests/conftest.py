"""
conftest.py

Shared pytest fixtures for the authentication test suite.
"""

import pytest

from src.database import database
from src.models.user import User
from src.models.client import Client
from src.models.contract import Contract
from src.models.event import Event


@pytest.fixture(scope="function")
def test_database():
    """
    Prepare a clean database for each test.
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
        ]
    )

    yield

    database.drop_tables(
        [
            Event,
            Contract,
            Client,
            User,
        ],
        safe=True,
    )

    database.close()