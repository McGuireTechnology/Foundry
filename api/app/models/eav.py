from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, UniqueConstraint
from sqlmodel import Column, Field, SQLModel

from app.services.ids import generate_ulid


class DataEntity(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("application_id", "api_name", name="uq_data_entity_app_api_name"),)

    id: str = Field(default_factory=generate_ulid, primary_key=True, index=True)
    application_id: str = Field(foreign_key="application.id", index=True)
    api_name: str = Field(max_length=120)
    display_name: str = Field(max_length=120)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class DataAttribute(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("entity_id", "api_name", name="uq_data_attribute_entity_api_name"),)

    id: str = Field(default_factory=generate_ulid, primary_key=True, index=True)
    entity_id: str = Field(foreign_key="dataentity.id", index=True)
    api_name: str = Field(max_length=120)
    display_name: str = Field(max_length=120)
    data_type: str = Field(max_length=30)
    is_required: bool = Field(default=False)
    is_unique: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class EntityRecord(SQLModel, table=True):
    id: str = Field(default_factory=generate_ulid, primary_key=True, index=True)
    entity_id: str = Field(foreign_key="dataentity.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AttributeValue(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("record_id", "attribute_id", name="uq_record_attribute"),)

    id: str = Field(default_factory=generate_ulid, primary_key=True, index=True)
    record_id: str = Field(foreign_key="entityrecord.id", index=True)
    attribute_id: str = Field(foreign_key="dataattribute.id", index=True)
    value_text: str | None = Field(default=None)
    value_number: float | None = Field(default=None)
    value_boolean: bool | None = Field(default=None)
    value_datetime: datetime | None = Field(default=None)
    value_json: dict[str, Any] | list[Any] | None = Field(default=None, sa_column=Column(JSON, nullable=True))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
