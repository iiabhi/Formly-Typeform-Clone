from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session


def test_health_ok(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_foreign_keys_enforced(db: Session) -> None:
    assert db.execute(text("PRAGMA foreign_keys")).scalar() == 1
