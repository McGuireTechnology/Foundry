from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, UniqueConstraint
from sqlmodel import Column, Field, SQLModel

from app.services.ids import generate_ulid


class OdsIdentityUser(SQLModel, table=True):
    __tablename__ = "ods_identity_user"
    __table_args__ = (UniqueConstraint("connection_id", "source_object_id", name="uq_ods_user_conn_source_object"),)

    id: str = Field(default_factory=generate_ulid, primary_key=True)
    org_id: str = Field(max_length=64, index=True)
    connection_id: str = Field(foreign_key="connector_connection.id", max_length=64, index=True)
    source_object_id: str = Field(max_length=255, index=True)
    distinguished_name: str | None = Field(default=None, max_length=2048)
    user_principal_name: str | None = Field(default=None, max_length=255)
    sam_account_name: str | None = Field(default=None, max_length=255)
    display_name: str | None = Field(default=None, max_length=255)
    mail: str | None = Field(default=None, max_length=255)
    department: str | None = Field(default=None, max_length=255)
    title: str | None = Field(default=None, max_length=255)
    account_enabled: bool = Field(default=True)
    source_created_at: datetime | None = Field(default=None)
    source_updated_at: datetime | None = Field(default=None)
    last_seen_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    is_deleted: bool = Field(default=False)
    deleted_at: datetime | None = Field(default=None)
    raw_payload_json: dict[str, Any] | list[Any] | None = Field(default=None, sa_column=Column(JSON, nullable=True))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class OdsIdentityComputer(SQLModel, table=True):
    __tablename__ = "ods_identity_computer"
    __table_args__ = (
        UniqueConstraint("connection_id", "source_object_id", name="uq_ods_computer_conn_source_object"),
    )

    id: str = Field(default_factory=generate_ulid, primary_key=True)
    org_id: str = Field(max_length=64, index=True)
    connection_id: str = Field(foreign_key="connector_connection.id", max_length=64, index=True)
    source_object_id: str = Field(max_length=255, index=True)
    distinguished_name: str | None = Field(default=None, max_length=2048)
    dns_host_name: str | None = Field(default=None, max_length=255)
    sam_account_name: str | None = Field(default=None, max_length=255)
    operating_system: str | None = Field(default=None, max_length=255)
    operating_system_version: str | None = Field(default=None, max_length=255)
    account_enabled: bool = Field(default=True)
    source_created_at: datetime | None = Field(default=None)
    source_updated_at: datetime | None = Field(default=None)
    last_seen_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    is_deleted: bool = Field(default=False)
    deleted_at: datetime | None = Field(default=None)
    raw_payload_json: dict[str, Any] | list[Any] | None = Field(default=None, sa_column=Column(JSON, nullable=True))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
