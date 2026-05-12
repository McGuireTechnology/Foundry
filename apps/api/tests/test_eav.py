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


def _auth_headers(client: TestClient) -> dict[str, str]:
    signup = client.post(
        "/users",
        headers=_headers(),
        json={"email": "eav@example.com", "password": "strongpass123"},
    )
    assert signup.status_code == 201

    signin = client.post(
        "/auth/token",
        headers=_headers(),
        json={"email": "eav@example.com", "password": "strongpass123"},
    )
    assert signin.status_code == 200
    token = signin.json()["access_token"]
    return {**_headers(), "Authorization": f"Bearer {token}"}


def test_eav_entity_attribute_record_flow() -> None:
    client = _create_client()
    headers = _auth_headers(client)

    app_resp = client.post(
        "/applications",
        headers=headers,
        json={"name": "CRM", "slug": "crm"},
    )
    assert app_resp.status_code == 201
    app_id = app_resp.json()["id"]

    entity_resp = client.post(
        "/tables",
        headers=headers,
        json={"application_id": app_id, "api_name": "contacts", "display_name": "Contacts"},
    )
    assert entity_resp.status_code == 201
    entity_id = entity_resp.json()["id"]

    attr_name = client.post(
        "/columns",
        headers=headers,
        json={
            "entity_id": entity_id,
            "api_name": "full_name",
            "display_name": "Full Name",
            "data_type": "text",
        },
    )
    assert attr_name.status_code == 201
    name_attr_id = attr_name.json()["id"]

    attr_age = client.post(
        "/columns",
        headers=headers,
        json={
            "entity_id": entity_id,
            "api_name": "age",
            "display_name": "Age",
            "data_type": "number",
        },
    )
    assert attr_age.status_code == 201
    age_attr_id = attr_age.json()["id"]

    record_resp = client.post(
        "/records",
        headers=headers,
        json={
            "entity_id": entity_id,
            "values": [
                {"attribute_id": name_attr_id, "value_text": "Alice Jones"},
                {"attribute_id": age_attr_id, "value_number": 34},
            ],
        },
    )
    assert record_resp.status_code == 201
    record_id = record_resp.json()["record"]["id"]
    assert len(record_resp.json()["values"]) == 2

    patch_resp = client.post(
        f"/values?record_id={record_id}",
        headers=headers,
        json=[{"attribute_id": age_attr_id, "value_number": 35}],
    )
    assert patch_resp.status_code == 201
    values = {item["attribute_id"]: item for item in patch_resp.json()}
    assert values[age_attr_id]["value_number"] == 35

    get_resp = client.get(f"/records/{record_id}", headers=headers)
    assert get_resp.status_code == 200
    values = {item["attribute_id"]: item for item in get_resp.json()["values"]}
    assert values[name_attr_id]["value_text"] == "Alice Jones"
    assert values[age_attr_id]["value_number"] == 35

    records_from_table = client.get(f"/tables/{entity_id}/records", headers=headers)
    assert records_from_table.status_code == 200
    records_from_query = client.get(f"/records?table_id={entity_id}", headers=headers)
    assert records_from_query.status_code == 200
    assert records_from_table.json() == records_from_query.json()

    columns_from_table = client.get(f"/tables/{entity_id}/columns", headers=headers)
    assert columns_from_table.status_code == 200
    columns_from_query = client.get(f"/columns?entity_id={entity_id}", headers=headers)
    assert columns_from_query.status_code == 200
    assert columns_from_table.json() == columns_from_query.json()

    values_from_column = client.get(f"/columns/{age_attr_id}/values", headers=headers)
    assert values_from_column.status_code == 200
    values_from_column_query = client.get(f"/values?column_id={age_attr_id}", headers=headers)
    assert values_from_column_query.status_code == 200
    assert values_from_column.json() == values_from_column_query.json()

    values_from_record = client.get(f"/records/{record_id}/values", headers=headers)
    assert values_from_record.status_code == 200
    values_from_record_query = client.get(f"/values?record_id={record_id}", headers=headers)
    assert values_from_record_query.status_code == 200
    assert values_from_record.json() == values_from_record_query.json()
