from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

from app.api.v1.endpoints import auth as auth_endpoints
from app.core import db as db_module
from app.main import app


def _headers() -> dict[str, str]:
    return {"X-API-Version": "v1"}


def _create_client() -> TestClient:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    db_module.engine = engine
    SQLModel.metadata.create_all(engine)
    auth_endpoints._login_attempts.clear()
    return TestClient(app)


def _auth_headers(client: TestClient, email: str = "crud@example.com") -> dict[str, str]:
    signup = client.post(
        "/users",
        headers=_headers(),
        json={"email": email, "password": "strongpass123"},
    )
    assert signup.status_code == 201

    signin = client.post(
        "/auth/token",
        headers=_headers(),
        json={"email": email, "password": "strongpass123"},
    )
    assert signin.status_code == 200
    token = signin.json()["access_token"]
    return {**_headers(), "Authorization": f"Bearer {token}"}


def test_applications_crud() -> None:
    client = _create_client()
    headers = _auth_headers(client)

    created = client.post(
        "/applications",
        headers=headers,
        json={"name": "Sales App", "slug": "sales-app", "description": "Sales workspace"},
    )
    assert created.status_code == 201
    app_id = created.json()["id"]

    listed = client.get("/applications", headers=headers)
    assert listed.status_code == 200
    assert any(item["id"] == app_id for item in listed.json())

    fetched = client.get(f"/applications/{app_id}", headers=headers)
    assert fetched.status_code == 200
    assert fetched.json()["slug"] == "sales-app"

    replaced = client.put(
        f"/applications/{app_id}",
        headers=headers,
        json={
            "name": "Sales Platform",
            "slug": "sales-platform",
            "description": "Replaced description",
            "is_active": False,
        },
    )
    assert replaced.status_code == 200
    assert replaced.json()["name"] == "Sales Platform"
    assert replaced.json()["slug"] == "sales-platform"
    assert replaced.json()["is_active"] is False

    updated = client.patch(
        f"/applications/{app_id}",
        headers=headers,
        json={"description": "Patched description"},
    )
    assert updated.status_code == 200
    assert updated.json()["description"] == "Patched description"

    deleted = client.delete(f"/applications/{app_id}", headers=headers)
    assert deleted.status_code == 204

    missing = client.get(f"/applications/{app_id}", headers=headers)
    assert missing.status_code == 404


def test_databases_crud() -> None:
    client = _create_client()
    headers = _auth_headers(client, email="dbcrud@example.com")

    created = client.post(
        "/databases",
        headers=headers,
        json={
            "name": "Primary DB",
            "slug": "primary-db",
        },
    )
    assert created.status_code == 201
    db_id = created.json()["id"]

    listed = client.get("/databases", headers=headers)
    assert listed.status_code == 200
    assert any(item["id"] == db_id for item in listed.json())

    fetched = client.get(f"/databases/{db_id}", headers=headers)
    assert fetched.status_code == 200
    assert fetched.json()["slug"] == "primary-db"

    replaced = client.put(
        f"/databases/{db_id}",
        headers=headers,
        json={
            "name": "Primary DB Replaced",
            "slug": "primary-db-replaced",
        },
    )
    assert replaced.status_code == 200
    assert replaced.json()["name"] == "Primary DB Replaced"
    assert replaced.json()["slug"] == "primary-db-replaced"

    updated = client.patch(
        f"/databases/{db_id}",
        headers=headers,
        json={"slug": "primary-db-patched"},
    )
    assert updated.status_code == 200
    assert updated.json()["slug"] == "primary-db-patched"

    deleted = client.delete(f"/databases/{db_id}", headers=headers)
    assert deleted.status_code == 204

    missing = client.get(f"/databases/{db_id}", headers=headers)
    assert missing.status_code == 404
