"""initial foundry api schema

Revision ID: 20260512_0001
Revises:
Create Date: 2026-05-12 13:30:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260512_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "application",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(op.f("ix_application_id"), "application", ["id"], unique=False)
    op.create_index(op.f("ix_application_slug"), "application", ["slug"], unique=False)

    op.create_table(
        "user",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("refresh_token_version", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_user_email"), "user", ["email"], unique=False)
    op.create_index(op.f("ix_user_id"), "user", ["id"], unique=False)

    op.create_table(
        "database",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(op.f("ix_database_id"), "database", ["id"], unique=False)
    op.create_index(op.f("ix_database_slug"), "database", ["slug"], unique=False)

    op.create_table(
        "dataentity",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("application_id", sa.String(), nullable=False),
        sa.Column("api_name", sa.String(length=120), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["application_id"], ["application.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("application_id", "api_name", name="uq_data_entity_app_api_name"),
    )
    op.create_index(op.f("ix_dataentity_application_id"), "dataentity", ["application_id"], unique=False)
    op.create_index(op.f("ix_dataentity_id"), "dataentity", ["id"], unique=False)

    op.create_table(
        "dataattribute",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("entity_id", sa.String(), nullable=False),
        sa.Column("api_name", sa.String(length=120), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("data_type", sa.String(length=30), nullable=False),
        sa.Column("is_required", sa.Boolean(), nullable=False),
        sa.Column("is_unique", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["entity_id"], ["dataentity.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("entity_id", "api_name", name="uq_data_attribute_entity_api_name"),
    )
    op.create_index(op.f("ix_dataattribute_entity_id"), "dataattribute", ["entity_id"], unique=False)
    op.create_index(op.f("ix_dataattribute_id"), "dataattribute", ["id"], unique=False)

    op.create_table(
        "entityrecord",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("entity_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["entity_id"], ["dataentity.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_entityrecord_entity_id"), "entityrecord", ["entity_id"], unique=False)
    op.create_index(op.f("ix_entityrecord_id"), "entityrecord", ["id"], unique=False)

    op.create_table(
        "attributevalue",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("record_id", sa.String(), nullable=False),
        sa.Column("attribute_id", sa.String(), nullable=False),
        sa.Column("value_text", sa.String(), nullable=True),
        sa.Column("value_number", sa.Float(), nullable=True),
        sa.Column("value_boolean", sa.Boolean(), nullable=True),
        sa.Column("value_datetime", sa.DateTime(timezone=True), nullable=True),
        sa.Column("value_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["attribute_id"], ["dataattribute.id"]),
        sa.ForeignKeyConstraint(["record_id"], ["entityrecord.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("record_id", "attribute_id", name="uq_record_attribute"),
    )
    op.create_index(op.f("ix_attributevalue_attribute_id"), "attributevalue", ["attribute_id"], unique=False)
    op.create_index(op.f("ix_attributevalue_id"), "attributevalue", ["id"], unique=False)
    op.create_index(op.f("ix_attributevalue_record_id"), "attributevalue", ["record_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_attributevalue_record_id"), table_name="attributevalue")
    op.drop_index(op.f("ix_attributevalue_id"), table_name="attributevalue")
    op.drop_index(op.f("ix_attributevalue_attribute_id"), table_name="attributevalue")
    op.drop_table("attributevalue")

    op.drop_index(op.f("ix_entityrecord_id"), table_name="entityrecord")
    op.drop_index(op.f("ix_entityrecord_entity_id"), table_name="entityrecord")
    op.drop_table("entityrecord")

    op.drop_index(op.f("ix_dataattribute_id"), table_name="dataattribute")
    op.drop_index(op.f("ix_dataattribute_entity_id"), table_name="dataattribute")
    op.drop_table("dataattribute")

    op.drop_index(op.f("ix_dataentity_id"), table_name="dataentity")
    op.drop_index(op.f("ix_dataentity_application_id"), table_name="dataentity")
    op.drop_table("dataentity")

    op.drop_index(op.f("ix_database_slug"), table_name="database")
    op.drop_index(op.f("ix_database_id"), table_name="database")
    op.drop_table("database")

    op.drop_index(op.f("ix_user_id"), table_name="user")
    op.drop_index(op.f("ix_user_email"), table_name="user")
    op.drop_table("user")

    op.drop_index(op.f("ix_application_slug"), table_name="application")
    op.drop_index(op.f("ix_application_id"), table_name="application")
    op.drop_table("application")
