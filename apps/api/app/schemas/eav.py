from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DataEntityCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    application_id: str
    api_name: str = Field(min_length=1, max_length=120)
    display_name: str = Field(min_length=1, max_length=120)


class DataEntityUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    application_id: str | None = None
    api_name: str | None = Field(default=None, min_length=1, max_length=120)
    display_name: str | None = Field(default=None, min_length=1, max_length=120)


class DataEntityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    application_id: str
    api_name: str
    display_name: str
    created_at: datetime
    updated_at: datetime


class DataAttributeCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    entity_id: str
    api_name: str = Field(min_length=1, max_length=120)
    display_name: str = Field(min_length=1, max_length=120)
    data_type: str = Field(min_length=1, max_length=30)
    is_required: bool = False
    is_unique: bool = False


class DataAttributeUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    api_name: str | None = Field(default=None, min_length=1, max_length=120)
    display_name: str | None = Field(default=None, min_length=1, max_length=120)
    data_type: str | None = Field(default=None, min_length=1, max_length=30)
    is_required: bool | None = None
    is_unique: bool | None = None


class DataAttributeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    entity_id: str
    api_name: str
    display_name: str
    data_type: str
    is_required: bool
    is_unique: bool
    created_at: datetime
    updated_at: datetime


class AttributeValueInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    attribute_id: str
    value_text: str | None = None
    value_number: float | None = None
    value_boolean: bool | None = None
    value_datetime: datetime | None = None
    value_json: dict[str, Any] | list[Any] | None = None

    @model_validator(mode="after")
    def validate_single_value(self) -> "AttributeValueInput":
        values = [self.value_text, self.value_number, self.value_boolean, self.value_datetime, self.value_json]
        populated = sum(value is not None for value in values)
        if populated != 1:
            raise ValueError("Exactly one value_* field must be set")
        return self


class EntityRecordCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    entity_id: str
    values: list[AttributeValueInput] = Field(default_factory=list)


class EntityRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    entity_id: str
    created_at: datetime
    updated_at: datetime


class AttributeValueRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    record_id: str
    attribute_id: str
    value_text: str | None
    value_number: float | None
    value_boolean: bool | None
    value_datetime: datetime | None
    value_json: dict[str, Any] | list[Any] | None
    created_at: datetime
    updated_at: datetime


class EntityRecordWithValuesRead(BaseModel):
    record: EntityRecordRead
    values: list[AttributeValueRead]
