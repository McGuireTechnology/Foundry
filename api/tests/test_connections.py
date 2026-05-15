from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.api.v1.endpoints import auth as auth_endpoints
from app.api.v1.endpoints import connections as connection_endpoints
from app.core import db as db_module
from app.models.identity import OdsIdentityComputer, OdsIdentityUser
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


def _auth_headers(client: TestClient, email: str = "connections@example.com") -> dict[str, str]:
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


def test_connections_support_multiple_same_type_and_independent_checkpoints() -> None:
    client = _create_client()
    headers = _auth_headers(client)
    connection_endpoints._build_ad_client = lambda _connection: _FakeAdClient()  # type: ignore[assignment]

    c1 = client.post(
        "/connections",
        headers=headers,
        json={
            "org_id": "org-1",
            "connector_type_slug": "active_directory",
            "name": "Corp AD",
            "slug": "corp-ad",
            "config_json": {
                "host": "ad1.example.com",
                "search_base": "DC=example,DC=com",
                "bind_dn": "CN=svc,OU=Svc,DC=example,DC=com",
                "bind_password": "secret",
            },
            "credentials_ref": "secret://ad/corp",
        },
    )
    assert c1.status_code == 201
    c1_id = c1.json()["id"]

    c2 = client.post(
        "/connections",
        headers=headers,
        json={
            "org_id": "org-1",
            "connector_type_slug": "active_directory",
            "name": "EMEA AD",
            "slug": "emea-ad",
            "config_json": {
                "host": "ad2.example.com",
                "search_base": "DC=emea,DC=example,DC=com",
                "bind_dn": "CN=svc,OU=Svc,DC=emea,DC=example,DC=com",
                "bind_password": "secret",
            },
            "credentials_ref": "secret://ad/emea",
        },
    )
    assert c2.status_code == 201
    c2_id = c2.json()["id"]

    sync1 = client.post(
        f"/connections/{c1_id}/sync",
        headers=headers,
        json={"entity_name": "users", "cursor_value": "2026-05-13T20:00:00Z"},
    )
    assert sync1.status_code == 202
    assert sync1.json()["connection_id"] == c1_id
    assert sync1.json()["checkpoint_entity_name"] == "users"
    assert sync1.json()["checkpoint_cursor_value"] == "2026-05-13T20:00:00Z"

    sync2 = client.post(
        f"/connections/{c2_id}/sync",
        headers=headers,
        json={"entity_name": "users", "cursor_value": "2026-05-13T21:00:00Z"},
    )
    assert sync2.status_code == 202
    assert sync2.json()["connection_id"] == c2_id
    assert sync2.json()["checkpoint_entity_name"] == "users"
    assert sync2.json()["checkpoint_cursor_value"] == "2026-05-13T21:00:00Z"

    sync1_groups = client.post(
        f"/connections/{c1_id}/sync",
        headers=headers,
        json={"entity_name": "computers", "cursor_value": "2026-05-13T20:10:00Z"},
    )
    assert sync1_groups.status_code == 202

    runs_for_c1_page1 = client.get(f"/connections/{c1_id}/sync-runs?limit=1", headers=headers)
    assert runs_for_c1_page1.status_code == 200
    runs_for_c1_page1_json = runs_for_c1_page1.json()
    assert len(runs_for_c1_page1_json["items"]) == 1
    assert runs_for_c1_page1_json["items"][0]["connection_id"] == c1_id
    assert runs_for_c1_page1_json["items"][0]["watermark_after"] == "2026-05-13T20:10:00Z"
    assert runs_for_c1_page1_json["page"]["next_cursor"] is not None

    runs_for_c1_page2 = client.get(
        f"/connections/{c1_id}/sync-runs?limit=1&cursor={runs_for_c1_page1_json['page']['next_cursor']}",
        headers=headers,
    )
    assert runs_for_c1_page2.status_code == 200
    runs_for_c1_page2_json = runs_for_c1_page2.json()
    assert len(runs_for_c1_page2_json["items"]) == 1
    assert runs_for_c1_page2_json["items"][0]["connection_id"] == c1_id
    assert runs_for_c1_page2_json["items"][0]["watermark_after"] == "2026-05-13T20:00:00Z"

    runs_for_c2 = client.get(f"/connections/{c2_id}/sync-runs", headers=headers)
    assert runs_for_c2.status_code == 200
    runs_for_c2_json = runs_for_c2.json()
    assert len(runs_for_c2_json["items"]) == 1
    assert runs_for_c2_json["items"][0]["connection_id"] == c2_id
    assert runs_for_c2_json["items"][0]["watermark_after"] == "2026-05-13T21:00:00Z"

    checkpoints_for_c1_page1 = client.get(f"/connections/{c1_id}/checkpoints?limit=1", headers=headers)
    assert checkpoints_for_c1_page1.status_code == 200
    checkpoints_for_c1_page1_json = checkpoints_for_c1_page1.json()
    assert len(checkpoints_for_c1_page1_json["items"]) == 1
    assert checkpoints_for_c1_page1_json["items"][0]["connection_id"] == c1_id
    assert checkpoints_for_c1_page1_json["items"][0]["entity_name"] == "computers"
    assert checkpoints_for_c1_page1_json["items"][0]["cursor_value"] == "2026-05-13T20:10:00Z"
    assert checkpoints_for_c1_page1_json["page"]["next_cursor"] is not None

    checkpoints_for_c1_page2 = client.get(
        f"/connections/{c1_id}/checkpoints?limit=1&cursor={checkpoints_for_c1_page1_json['page']['next_cursor']}",
        headers=headers,
    )
    assert checkpoints_for_c1_page2.status_code == 200
    checkpoints_for_c1_page2_json = checkpoints_for_c1_page2.json()
    assert len(checkpoints_for_c1_page2_json["items"]) == 1
    assert checkpoints_for_c1_page2_json["items"][0]["connection_id"] == c1_id
    assert checkpoints_for_c1_page2_json["items"][0]["entity_name"] == "users"
    assert checkpoints_for_c1_page2_json["items"][0]["cursor_value"] == "2026-05-13T20:00:00Z"

    checkpoints_for_c2 = client.get(f"/connections/{c2_id}/checkpoints", headers=headers)
    assert checkpoints_for_c2.status_code == 200
    checkpoints_for_c2_json = checkpoints_for_c2.json()
    assert len(checkpoints_for_c2_json["items"]) == 1
    assert checkpoints_for_c2_json["items"][0]["connection_id"] == c2_id
    assert checkpoints_for_c2_json["items"][0]["entity_name"] == "users"
    assert checkpoints_for_c2_json["items"][0]["cursor_value"] == "2026-05-13T21:00:00Z"

    listed = client.get("/connections", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 2


class _FakeAdClient:
    def test_connection(self) -> None:
        return None

    def fetch_users(self) -> list[dict[str, str]]:
        return [
            {
                "objectGUID": "user-guid-1",
                "distinguishedName": "CN=Alice,OU=Users,DC=example,DC=com",
                "userPrincipalName": "alice@example.com",
                "sAMAccountName": "alice",
                "displayName": "Alice Example",
                "mail": "alice@example.com",
                "department": "IT",
                "title": "Engineer",
                "whenCreated": "2026-05-10T00:00:00+00:00",
                "whenChanged": "2026-05-14T00:00:00+00:00",
                "userAccountControl": "512",
            }
        ]

    def fetch_computers(self) -> list[dict[str, str]]:
        return [
            {
                "objectGUID": "computer-guid-1",
                "distinguishedName": "CN=WS-01,OU=Computers,DC=example,DC=com",
                "dNSHostName": "ws-01.example.com",
                "sAMAccountName": "WS-01$",
                "operatingSystem": "Windows 11",
                "operatingSystemVersion": "10.0",
                "whenCreated": "2026-05-11T00:00:00+00:00",
                "whenChanged": "2026-05-14T00:00:00+00:00",
                "userAccountControl": "4128",
            }
        ]


def test_active_directory_test_and_sync_users_computers(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    client = _create_client()
    headers = _auth_headers(client, email="ad@example.com")
    monkeypatch.setattr(connection_endpoints, "_build_ad_client", lambda _connection: _FakeAdClient())

    created = client.post(
        "/connections",
        headers=headers,
        json={
            "org_id": "org-ad",
            "connector_type_slug": "active_directory",
            "name": "Corp AD",
            "slug": "corp-ad",
            "config_json": {
                "host": "ad1.example.com",
                "search_base": "DC=example,DC=com",
                "bind_dn": "CN=svc,OU=Svc,DC=example,DC=com",
                "bind_password": "secret",
            },
        },
    )
    assert created.status_code == 201
    connection_id = created.json()["id"]

    tested = client.post(f"/connections/{connection_id}/test", headers=headers)
    assert tested.status_code == 200
    assert tested.json()["status"] == "ok"

    users_sync = client.post(
        f"/connections/{connection_id}/sync",
        headers=headers,
        json={"entity_name": "users"},
    )
    assert users_sync.status_code == 202

    computers_sync = client.post(
        f"/connections/{connection_id}/sync",
        headers=headers,
        json={"entity_name": "computers"},
    )
    assert computers_sync.status_code == 202

    with Session(db_module.engine) as session:
        users = list(
            session.exec(
                select(OdsIdentityUser).where(OdsIdentityUser.connection_id == connection_id)
            ).all()
        )
        computers = list(
            session.exec(
                select(OdsIdentityComputer).where(OdsIdentityComputer.connection_id == connection_id)
            ).all()
        )

    assert len(users) == 1
    assert users[0].sam_account_name == "alice"
    assert len(computers) == 1
    assert computers[0].dns_host_name == "ws-01.example.com"
