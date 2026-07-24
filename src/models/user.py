from peewee import BooleanField, CharField, Model

from src.core.database import database


class User(Model):
    full_name = CharField(max_length=255)
    email = CharField(max_length=255, unique=True)
    password_hash = CharField(max_length=255)

    department = CharField(max_length=50)
    is_active = BooleanField(default=True)

    class Meta:
        database = database
        table_name = "users"