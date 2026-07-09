"""
database.py

Role:
- Configure the SQLite database.
- Expose the shared database connection.

All models use this connection.
"""

from peewee import SqliteDatabase

from src.config import DATABASE_PATH

database = SqliteDatabase(DATABASE_PATH)