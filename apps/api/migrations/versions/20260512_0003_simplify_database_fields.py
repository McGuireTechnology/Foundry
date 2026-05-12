"""simplify database fields to name and slug

Revision ID: 20260512_0003
Revises: 20260512_0002
Create Date: 2026-05-12 15:10:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260512_0003"
down_revision: str | None = "20260512_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("database")}

    if "slug" not in columns:
        if "database_name" in columns:
            op.add_column("database", sa.Column("slug", sa.String(length=120), nullable=True))
            if dialect == "postgresql":
                op.execute('UPDATE "database" SET slug = lower(regexp_replace(database_name, \'[^a-zA-Z0-9_\\-]+\', \'-\', \'g\')) WHERE slug IS NULL')
            else:
                op.execute("UPDATE database SET slug = database_name WHERE slug IS NULL")
            op.alter_column("database", "slug", nullable=False)
        else:
            op.add_column("database", sa.Column("slug", sa.String(length=120), nullable=False, server_default="database"))
            op.alter_column("database", "slug", server_default=None)

    op.create_index("ix_database_slug", "database", ["slug"], unique=False)
    op.create_unique_constraint("uq_database_slug", "database", ["slug"])

    for column_name in ("engine", "database_name", "host", "port"):
        if column_name in columns:
            op.drop_column("database", column_name)


def downgrade() -> None:
    op.add_column("database", sa.Column("engine", sa.String(length=50), nullable=True))
    op.add_column("database", sa.Column("database_name", sa.String(length=120), nullable=True))
    op.add_column("database", sa.Column("host", sa.String(length=255), nullable=True))
    op.add_column("database", sa.Column("port", sa.Integer(), nullable=True))
    op.drop_constraint("uq_database_slug", "database", type_="unique")
    op.drop_index("ix_database_slug", table_name="database")
    op.drop_column("database", "slug")
