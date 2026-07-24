"""
Create the SQLite tables required by the Epic Events CRM.

Run from the project root with:

    python -m src.utils.create_db
"""

import typer

from src.core.database import database
from src.models.client import Client
from src.models.contract import Contract
from src.models.event import Event
from src.models.user import User


def create_database() -> None:
    """Create all application database tables safely."""

    database.connect(
        reuse_if_open=True,
    )

    try:
        database.create_tables(
            [
                User,
                Client,
                Contract,
                Event,
            ],
            safe=True,
        )

        typer.echo(
            "Database initialized successfully."
        )

    finally:
        if not database.is_closed():
            database.close()


if __name__ == "__main__":
    typer.run(create_database)
