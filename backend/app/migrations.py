"""Additive, transactional migration. Never drops images or interaction data."""
from sqlalchemy import inspect, text

from .db import Base
from . import models  # noqa: F401 - register tables


def migrate(engine):
    with engine.begin() as connection:
        if connection.dialect.name == "postgresql":
            connection.execute(text("SELECT pg_advisory_xact_lock(781423095)"))
        connection.execute(text("CREATE TABLE IF NOT EXISTS gallery_migration (version INTEGER PRIMARY KEY)"))
        if connection.execute(text("SELECT version FROM gallery_migration WHERE version=1")).first():
            return
        inspector = inspect(connection)
        if inspector.has_table("image"):
            columns = {column["name"] for column in inspector.get_columns("image")}
            for name in ("likes_count", "comments_count", "revision"):
                if name not in columns:
                    connection.execute(text(
                        f"ALTER TABLE image ADD COLUMN {name} BIGINT NOT NULL DEFAULT 0 CHECK ({name} >= 0)"
                    ))
        Base.metadata.create_all(connection)
        connection.execute(text("INSERT INTO gallery_migration (version) VALUES (1)"))
