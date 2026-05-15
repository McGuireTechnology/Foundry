from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ConnectionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    org_id: str = Field(min_length=1, max_length=64)
    connector_type_slug: str = Field(min_length=1, max_length=120)
    connector_type_name: str | None = Field(default=None, min_length=1, max_length=120)
    name: str = Field(min_length=1, max_length=120)
    slug: str = Field(min_length=1, max_length=120)
    config_json: dict[str, Any] | list[Any]
    credentials_ref: str | None = Field(default=None, max_length=255)


class ConnectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    org_id: str
    connector_type_id: str
    name: str
    slug: str
    status: str
    config_json: dict[str, Any] | list[Any]
    credentials_ref: str | None
    last_synced_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ConnectionSyncRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entity_name: str = Field(default="users", min_length=1, max_length=64)
    cursor_value: str | None = Field(default=None, max_length=255)


class ConnectionTestResponse(BaseModel):
    connection_id: str
    connector_type_slug: str
    status: str
    message: str


class ConnectionSyncResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    run_id: str
    connection_id: str
    org_id: str
    status: str
    run_type: str
    started_at: datetime
    ended_at: datetime
    checkpoint_entity_name: str
    checkpoint_cursor_value: str | None


class ConnectionSyncRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    org_id: str
    connection_id: str
    run_type: str
    status: str
    started_at: datetime
    ended_at: datetime | None
    watermark_before: str | None
    watermark_after: str | None
    records_read: int
    records_written: int
    records_failed: int
    metadata_json: dict[str, Any] | list[Any] | None
    created_at: datetime


class ConnectionSyncCheckpointRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    org_id: str
    connection_id: str
    entity_name: str
    cursor_value: str | None
    cursor_updated_at: datetime | None
    updated_at: datetime


class CursorPageMeta(BaseModel):
    next_cursor: str | None


class ConnectionSyncRunPage(BaseModel):
    items: list[ConnectionSyncRunRead]
    page: CursorPageMeta


class ConnectionSyncCheckpointPage(BaseModel):
    items: list[ConnectionSyncCheckpointRead]
    page: CursorPageMeta
