from datetime import datetime

from peewee import (
    BooleanField,
    DateTimeField,
    DecimalField,
    ForeignKeyField,
    Model,
)

from src.core.database import database
from src.models.client import Client
from src.models.user import User


class Contract(Model):
    client = ForeignKeyField(
        Client,
        backref="contracts",
        on_delete="RESTRICT"
    )

    sales_contact = ForeignKeyField(
        User,
        backref="contracts",
        on_delete="RESTRICT"
    )

    total_amount = DecimalField(max_digits=10, decimal_places=2)
    amount_due = DecimalField(max_digits=10, decimal_places=2)

    is_signed = BooleanField(default=False)

    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = database
        table_name = "contracts"