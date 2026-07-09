from src.database import database
from src.models.user import User
from src.models.client import Client
from src.models.contract import Contract
from src.models.event import Event


def test_database_tables():
    database.connect(reuse_if_open=True)

    tables = database.get_tables()

    assert User._meta.table_name in tables
    assert Client._meta.table_name in tables
    assert Contract._meta.table_name in tables
    assert Event._meta.table_name in tables

    database.close()