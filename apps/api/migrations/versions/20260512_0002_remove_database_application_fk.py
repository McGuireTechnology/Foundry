"""remove database application foreign key

Revision ID: 20260512_0002
Revises: 20260512_0001
Create Date: 2026-05-12 14:40:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260512_0002"
down_revision: str | None = "20260512_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None
# Alembic reads these module-level identifiers dynamically.
_ = (revision, down_revision, branch_labels, depends_on)


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "postgresql":
        op.execute(
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
        op.execute('DROP INDEX IF EXISTS ix_database_application_id')
        op.execute('ALTER TABLE "database" DROP COLUMN IF EXISTS application_id')
    else:
        inspector = sa.inspect(bind)
        columns = {column["name"] for column in inspector.get_columns("database")}
        if "application_id" in columns:
            op.drop_column("database", "application_id")


def downgrade() -> None:
    op.add_column("database", sa.Column("application_id", sa.String(), nullable=True))
    op.create_index("ix_database_application_id", "database", ["application_id"], unique=False)
