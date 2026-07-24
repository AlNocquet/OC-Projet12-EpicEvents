"""
database.py

Role:
- Configure the SQLite database.
- Expose the shared database connection.
- Enforce foreign-key constraints.

All models use this connection.
"""

from peewee import SqliteDatabase

from src.core.config import DATABASE_PATH


database = SqliteDatabase(
    DATABASE_PATH,
    pragmas={
        "foreign_keys": 1,
    },
)