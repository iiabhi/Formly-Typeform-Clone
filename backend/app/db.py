from collections.abc import Iterator
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings


class Base(DeclarativeBase):
    pass


def make_engine(url: str) -> Engine:
    """Create an engine; SQLite needs a thread flag and FK enforcement on every connection."""
    is_sqlite = url.startswith("sqlite")
    in_memory = url in ("sqlite://", "sqlite:///:memory:")
    engine = create_engine(
        url,
        connect_args={"check_same_thread": False} if is_sqlite else {},
        # An in-memory DB lives per connection, so share a single one.
        poolclass=StaticPool if in_memory else None,
    )
    if is_sqlite:

        @event.listens_for(engine, "connect")
        def _enable_foreign_keys(dbapi_connection: Any, _record: Any) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


engine = make_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session
