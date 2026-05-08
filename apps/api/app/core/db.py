from sqlalchemy import inspect
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

engine = create_engine(settings.database_url, echo=False)


def _drop_legacy_username_column() -> None:
    inspector = inspect(engine)
    if "user" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("user")}
    if "username" not in columns:
        return

    with engine.begin() as connection:
        connection.exec_driver_sql('ALTER TABLE "user" DROP COLUMN username')


def init_db() -> None:
    # Ensure SQLModel metadata includes all table models before create_all.
    from app.models import User  # noqa: F401

    SQLModel.metadata.create_all(engine)
    _drop_legacy_username_column()


def get_session() -> Session:
    with Session(engine) as session:
        yield session
