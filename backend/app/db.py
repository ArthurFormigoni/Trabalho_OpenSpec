from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine_options = {
    "connect_args": connect_args,
    "pool_pre_ping": True,
}
if not settings.database_url.startswith("sqlite"):
    # Aiven's shared plans have a small connection limit. Keep one small,
    # reusable pool per Render instance instead of SQLAlchemy's default burst.
    engine_options.update(pool_size=2, max_overflow=0, pool_timeout=10, pool_recycle=300, pool_use_lifo=True)
engine = create_engine(settings.database_url, **engine_options)
if engine.dialect.name == "sqlite":
    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
