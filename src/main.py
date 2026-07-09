import typer

from src.database import database
from src.models.user import User
from src.models.client import Client
from src.models.contract import Contract
from src.models.event import Event

app = typer.Typer()


@app.command()
def init_db():
    """Create database tables."""
    database.connect()
    database.create_tables([
        User,
        Client,
        Contract,
        Event,
    ])
    database.close()
    typer.echo("Database initialized successfully.")


if __name__ == "__main__":
    app()