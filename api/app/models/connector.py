from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, UniqueConstraint
from sqlmodel import Column, Field, SQLModel

from app.services.ids import generate_ulid


class ConnectorType(SQLModel, table=True):
    __tablename__ = "connector_type"

    id: str = Field(default_factory=generate_ulid, primary_key=True, index=True)
    name: str = Field(max_length=120)
    slug: str = Field(max_length=120, unique=True, index=True)
    description: str | None = Field(default=None, max_length=500)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ConnectorConnection(SQLModel, table=True):
    __tablename__ = "connector_connection"
    __table_args__ = (UniqueConstraint("org_id", "slug", name="uq_connector_connection_org_slug"),)

    id: str = Field(default_factory=generate_ulid, primary_key=True, index=True)
    org_id: str = Field(max_length=64, index=True)
    connector_type_id: str = Field(foreign_key="connector_type.id", index=True, max_length=64)
    name: str = Field(max_length=120)
    slug: str = Field(max_length=120)
    status: str = Field(default="active", max_length=32)
    config_json: dict[str, Any] | list[Any] = Field(sa_column=Column(JSON, nullable=False))
    credentials_ref: str | None = Field(default=None, max_length=255)
    last_synced_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ConnectorSyncRun(SQLModel, table=True):
    __tablename__ = "connector_sync_run"

    id: str = Field(default_factory=generate_ulid, primary_key=True, index=True)
    org_id: str = Field(max_length=64, index=True)
    connection_id: str = Field(foreign_key="connector_connection.id", max_length=64, index=True)
    run_type: str = Field(max_length=32)
    status: str = Field(max_length=32)
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    ended_at: datetime | None = Field(default=None)
    watermark_before: str | None = Field(default=None, max_length=128)
    watermark_after: str | None = Field(default=None, max_length=128)
    records_read: int = Field(default=0)
    records_written: int = Field(default=0)
    records_failed: int = Field(default=0)
    metadata_json: dict[str, Any] | list[Any] | None = Field(default=None, sa_column=Column(JSON, nullable=True))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ConnectorSyncCheckpoint(SQLModel, table=True):
    __tablename__ = "connector_sync_checkpoint"
    __table_args__ = (UniqueConstraint("connection_id", "entity_name", name="uq_sync_checkpoint_conn_entity"),)

    id: str = Field(default_factory=generate_ulid, primary_key=True)
    org_id: str = Field(max_length=64, index=True)
    connection_id: str = Field(foreign_key="connector_connection.id", max_length=64, index=True)
    entity_name: str = Field(max_length=64)
    cursor_value: str | None = Field(default=None, max_length=255)
    cursor_updated_at: datetime | None = Field(default=None)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

