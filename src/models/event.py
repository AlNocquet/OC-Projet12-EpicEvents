from peewee import (
    CharField,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    Model,
    TextField,
)

from src.database import database
from src.models.contract import Contract
from src.models.user import User


class Event(Model):
    contract = ForeignKeyField(
        Contract,
        backref="events",
        on_delete="RESTRICT"
    )

    support_contact = ForeignKeyField(
        User,
        backref="events",
        on_delete="SET NULL",
        null=True
    )

    event_name = CharField(max_length=255)
    location = CharField(max_length=255)
    attendees = IntegerField()
    event_start = DateTimeField()
    event_end = DateTimeField()
    notes = TextField(null=True)

    class Meta:
        database = database
        table_name = "events"