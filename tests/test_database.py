"""
Tests for the application database structure.
"""

from src.models.client import Client
from src.models.contract import Contract
from src.models.event import Event
from src.models.user import User


def test_database_tables(
    test_database,
):
    """All application tables exist in the isolated test database."""

    tables = test_database.get_tables()

    assert User._meta.table_name in tables
    assert Client._meta.table_name in tables
    assert Contract._meta.table_name in tables
    assert Event._meta.table_name in tables
