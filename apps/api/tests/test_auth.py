from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

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


def test_signup_rejects_unprompted_fields() -> None:
    client = _create_client()
    response = client.post(
        "/users",
        headers=_headers(),
        json={"email": "strict@example.com", "password": "strongpass123", "is_active": True},
    )
    assert response.status_code == 422


def test_users_endpoints_require_authentication() -> None:
    client = _create_client()
    client.post(
        "/users",
        headers=_headers(),
        json={"email": "private@example.com", "password": "strongpass123"},
    )

    listed = client.get("/users", headers=_headers())
    assert listed.status_code == 401

    fetched = client.get("/users/some-id", headers=_headers())
    assert fetched.status_code == 401


def test_users_endpoints_allow_authenticated_access() -> None:
    client = _create_client()
    signup = client.post(
        "/users",
        headers=_headers(),
        json={"email": "member@example.com", "password": "strongpass123"},
    )
    assert signup.status_code == 201

    signin = client.post(
        "/auth/token",
        headers=_headers(),
        json={"email": "member@example.com", "password": "strongpass123"},
    )
    assert signin.status_code == 200
    token = signin.json()["access_token"]
    auth_headers = {**_headers(), "Authorization": f"Bearer {token}"}

    listed = client.get("/users", headers=auth_headers)
    assert listed.status_code == 200
    assert any(user["email"] == "member@example.com" for user in listed.json())

    user_id = signup.json()["id"]
    fetched = client.get(f"/users/{user_id}", headers=auth_headers)
    assert fetched.status_code == 200
    assert fetched.json()["email"] == "member@example.com"


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


def test_password_reset_invalidates_existing_refresh_tokens() -> None:
    client = _create_client()
    client.post(
        "/users",
        headers=_headers(),
        json={"email": "revoke@example.com", "password": "oldpassword123"},
    )

    signin = client.post(
        "/auth/token",
        headers=_headers(),
        json={"email": "revoke@example.com", "password": "oldpassword123"},
    )
    assert signin.status_code == 200
    old_refresh_token = signin.json()["refresh_token"]

    forgot = client.post(
        "/auth/forgot-password",
        headers=_headers(),
        json={"email": "revoke@example.com"},
    )
    token = forgot.json().get("reset_token")
    assert token

    reset = client.post(
        "/auth/reset-password",
        headers=_headers(),
        json={"token": token, "new_password": "newpassword123"},
    )
    assert reset.status_code == 200

    refreshed = client.post(
        "/auth/refresh",
        headers=_headers(),
        json={"refresh_token": old_refresh_token},
    )
    assert refreshed.status_code == 401


def test_refresh_fails_for_inactive_user() -> None:
    client = _create_client()
    signup = client.post(
        "/users",
        headers=_headers(),
        json={"email": "inactive@example.com", "password": "strongpass123"},
    )
    assert signup.status_code == 201

    signin = client.post(
        "/auth/token",
        headers=_headers(),
        json={"email": "inactive@example.com", "password": "strongpass123"},
    )
    refresh_token = signin.json()["refresh_token"]

    user_id = signup.json()["id"]
    from app.models.user import User

    with Session(db_module.engine) as session:
        user = session.get(User, user_id)
        assert user is not None
        user.is_active = False
        session.add(user)
        session.commit()

    refreshed = client.post(
        "/auth/refresh",
        headers=_headers(),
        json={"refresh_token": refresh_token},
    )
    assert refreshed.status_code == 401


def test_email_is_normalized_on_signup_and_signin() -> None:
    client = _create_client()
    signup = client.post(
        "/users",
        headers=_headers(),
        json={"email": "  MixedCase@Example.com  ", "password": "strongpass123"},
    )
    assert signup.status_code == 201
    assert signup.json()["email"] == "mixedcase@example.com"

    duplicate = client.post(
        "/users",
        headers=_headers(),
        json={"email": "mixedcase@example.com", "password": "anotherpass123"},
    )
    assert duplicate.status_code == 409

    signin = client.post(
        "/auth/token",
        headers=_headers(),
        json={"email": "MIXEDCASE@example.com", "password": "strongpass123"},
    )
    assert signin.status_code == 200
