from sqlmodel import Field, SQLModel

from app.services.ids import generate_ulid


class User(SQLModel, table=True):
    id: str = Field(default_factory=generate_ulid, primary_key=True, index=True)
    email: str = Field(index=True, unique=True, max_length=255)
    hashed_password: str
    is_active: bool = Field(default=True)
    refresh_token_version: int = Field(default=0)
