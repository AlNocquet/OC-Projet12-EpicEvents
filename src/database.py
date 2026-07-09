from peewee import SqliteDatabase

from src.config import DATABASE_PATH

database = SqliteDatabase(DATABASE_PATH)