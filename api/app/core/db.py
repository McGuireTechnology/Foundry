from sqlalchemy import inspect
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

engine = create_engine(settings.database_url, echo=False)


def _reconcile_user_table_columns() -> None:
    inspector = inspect(engine)
    if "user" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("user")}

    with engine.begin() as connection:
        if "refresh_token_version" not in columns:
            connection.exec_driver_sql(
                'ALTER TABLE "user" ADD COLUMN refresh_token_version INTEGER NOT NULL DEFAULT 0'
            )
        if "username" in columns:
            connection.exec_driver_sql('ALTER TABLE "user" DROP COLUMN username')


def _reconcile_database_table_columns() -> None:
    if engine.dialect.name != "postgresql":
        return

    inspector = inspect(engine)
    if "database" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("database")}
    with engine.begin() as connection:
        if "application_id" in columns:
            connection.exec_driver_sql(
                """
                DO $$
                DECLARE
                  constraint_name text;
                BEGIN
                  FOR constraint_name IN
                    SELECT tc.constraint_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                      ON tc.constraint_name = kcu.constraint_name
                     AND tc.table_schema = kcu.table_schema
                    WHERE tc.table_name = 'database'
                      AND tc.constraint_type = 'FOREIGN KEY'
                      AND kcu.column_name = 'application_id'
                  LOOP
                    EXECUTE 'ALTER TABLE "database" DROP CONSTRAINT ' || quote_ident(constraint_name);
                  END LOOP;
                END $$;
                """
            )
            connection.exec_driver_sql("DROP INDEX IF EXISTS ix_database_application_id")
            connection.exec_driver_sql('ALTER TABLE "database" DROP COLUMN IF EXISTS application_id')

        if "slug" not in columns:
            if "database_name" in columns:
                connection.exec_driver_sql('ALTER TABLE "database" ADD COLUMN slug VARCHAR(120)')
                connection.exec_driver_sql(
                    """
                    UPDATE "database"
                    SET slug = lower(regexp_replace(database_name, '[^a-zA-Z0-9_\\-]+', '-', 'g'))
                    WHERE slug IS NULL
                    """
                )
                connection.exec_driver_sql('ALTER TABLE "database" ALTER COLUMN slug SET NOT NULL')
            else:
                connection.exec_driver_sql('ALTER TABLE "database" ADD COLUMN slug VARCHAR(120) NOT NULL DEFAULT \'database\'')
                connection.exec_driver_sql('ALTER TABLE "database" ALTER COLUMN slug DROP DEFAULT')
            connection.exec_driver_sql("CREATE UNIQUE INDEX IF NOT EXISTS uq_database_slug ON \"database\" (slug)")
            connection.exec_driver_sql("CREATE INDEX IF NOT EXISTS ix_database_slug ON \"database\" (slug)")

        connection.exec_driver_sql('ALTER TABLE "database" DROP COLUMN IF EXISTS engine')
        connection.exec_driver_sql('ALTER TABLE "database" DROP COLUMN IF EXISTS database_name')
        connection.exec_driver_sql('ALTER TABLE "database" DROP COLUMN IF EXISTS host')
        connection.exec_driver_sql('ALTER TABLE "database" DROP COLUMN IF EXISTS port')


def init_db() -> None:
    # Ensure SQLModel metadata includes all table models before create_all.
    from app.models import (  # noqa: F401
        Application,
        AttributeValue,
        ConnectorConnection,
        ConnectorSyncCheckpoint,
        ConnectorSyncRun,
        ConnectorType,
        DataAttribute,
        DataEntity,
        Database,
        EntityRecord,
        OdsIdentityComputer,
        OdsIdentityUser,
        User,
    )

    SQLModel.metadata.create_all(engine)
    _reconcile_user_table_columns()
    _reconcile_database_table_columns()


def get_session() -> Session:
    with Session(engine) as session:
        yield session
