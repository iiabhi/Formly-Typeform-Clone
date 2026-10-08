from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

import app.models  # noqa: F401  (registers tables on Base)
from app.db import Base, get_db, make_engine
from app.main import app


@pytest.fixture()
def db() -> Iterator[Session]:
    """Fresh in-memory SQLite per test."""
    engine = make_engine("sqlite://")
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)() as session:
        yield session
    engine.dispose()


@pytest.fixture()
def client(db: Session) -> Iterator[TestClient]:
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app)
    app.dependency_overrides.clear()
