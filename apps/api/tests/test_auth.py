from collections.abc import Generator

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


def test_signup_and_signin_happy_path() -> None:
    client = _create_client()
    signup = client.post(
        "/users",
        headers=_headers(),
        json={"email": "happy@example.com", "password": "strongpass123"},
    )
    assert signup.status_code == 201

    signin = client.post(
        "/auth/token",
        headers=_headers(),
        json={"email": "happy@example.com", "password": "strongpass123"},
    )
    assert signin.status_code == 200
    payload = signin.json()
    assert payload["access_token"]
    assert payload["refresh_token"]
    assert payload["token_type"] == "bearer"


def test_version_header_required() -> None:
    client = _create_client()
    response = client.post("/users", json={"email": "noheader@example.com", "password": "strongpass123"})
    assert response.status_code == 400
    assert "Invalid API version" in response.json()["detail"]


def test_forgot_password_generic_message() -> None:
    client = _create_client()
    response = client.post(
        "/auth/forgot-password",
        headers=_headers(),
        json={"email": "missing@example.com"},
    )
    assert response.status_code == 200
    assert "If an account exists" in response.json()["message"]


def test_login_lockout_policy() -> None:
    client = _create_client()
    client.post(
        "/users",
        headers=_headers(),
        json={"email": "lockout@example.com", "password": "goodpassword123"},
    )

    for _ in range(5):
        failed = client.post(
            "/auth/token",
            headers=_headers(),
            json={"email": "lockout@example.com", "password": "badpassword"},
        )
        assert failed.status_code == 401

    locked = client.post(
        "/auth/token",
        headers=_headers(),
        json={"email": "lockout@example.com", "password": "goodpassword123"},
    )
    assert locked.status_code == 429
    assert "Too many failed attempts" in locked.json()["detail"]


def test_reset_password_flow() -> None:
    client = _create_client()
    client.post(
        "/users",
        headers=_headers(),
        json={"email": "reset@example.com", "password": "oldpassword123"},
    )

    forgot = client.post(
        "/auth/forgot-password",
        headers=_headers(),
        json={"email": "reset@example.com"},
    )
    assert forgot.status_code == 200
    token = forgot.json().get("reset_token")
    assert token

    reset = client.post(
        "/auth/reset-password",
        headers=_headers(),
        json={"token": token, "new_password": "newpassword123"},
    )
    assert reset.status_code == 200

    signin = client.post(
        "/auth/token",
        headers=_headers(),
        json={"email": "reset@example.com", "password": "newpassword123"},
    )
    assert signin.status_code == 200
