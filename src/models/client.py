from peewee import CharField, DateTimeField, ForeignKeyField, Model
from datetime import datetime

from src.database import database
from src.models.user import User


class Client(Model):
    full_name = CharField(max_length=255)
    email = CharField(max_length=255, unique=True)
    phone = CharField(max_length=30)
    company_name = CharField(max_length=255)

    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    sales_contact = ForeignKeyField(
        User,
        backref="clients",
        on_delete="RESTRICT"
    )

    class Meta:
        database = database
        table_name = "clients"