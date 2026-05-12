from datetime import UTC, datetime

from sqlmodel import Field, SQLModel

from app.services.ids import generate_ulid


class Database(SQLModel, table=True):
    id: str = Field(default_factory=generate_ulid, primary_key=True, index=True)
    name: str = Field(max_length=120)
    slug: str = Field(max_length=120, unique=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
