from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

from app.api.v1.endpoints import auth as auth_endpoints
from app.core import db as db_module
from app.main import app


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


def test_auth_token_preflight_allows_local_web_origin() -> None:
    client = _create_client()
    origin = "http://localhost:5173"
    response = client.options(
        "/auth/token",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,x-api-version",
        },
    )

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == origin
    assert response.headers.get("access-control-allow-credentials") == "true"


def test_auth_token_response_includes_cors_headers_for_browser_origin() -> None:
    client = _create_client()
    origin = "http://localhost:5173"
    response = client.post(
        "/auth/token",
        headers={
            "Origin": origin,
            "Content-Type": "application/json",
            "X-API-Version": "v1",
        },
        json={"email": "missing@example.com", "password": "wrongpassword"},
    )

    assert response.status_code == 401
    assert response.headers.get("access-control-allow-origin") == origin
    assert response.headers.get("access-control-allow-credentials") == "true"
