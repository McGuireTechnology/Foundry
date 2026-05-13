"""add connection instances and active directory ods tables

Revision ID: 20260513_0004
Revises: 20260512_0003
Create Date: 2026-05-13 15:05:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260513_0004"
down_revision: str | None = "20260512_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None
_ = (revision, down_revision, branch_labels, depends_on)


def upgrade() -> None:
    op.create_table(
        "connector_type",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_connector_type_slug"),
    )
    op.create_index(op.f("ix_connector_type_id"), "connector_type", ["id"], unique=False)
    op.create_index(op.f("ix_connector_type_slug"), "connector_type", ["slug"], unique=False)

    op.create_table(
        "connector_connection",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("org_id", sa.String(length=64), nullable=False),
        sa.Column("connector_type_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default=sa.text("'active'")),
        sa.Column("config_json", sa.JSON(), nullable=False),
        sa.Column("credentials_ref", sa.String(length=255), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["connector_type_id"], ["connector_type.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("org_id", "slug", name="uq_connector_connection_org_slug"),
    )
    op.create_index(op.f("ix_connector_connection_id"), "connector_connection", ["id"], unique=False)
    op.create_index(op.f("ix_connector_connection_org_id"), "connector_connection", ["org_id"], unique=False)
    op.create_index(
        op.f("ix_connector_connection_connector_type_id"),
        "connector_connection",
        ["connector_type_id"],
        unique=False,
    )

    op.create_table(
        "connector_sync_run",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("org_id", sa.String(length=64), nullable=False),
        sa.Column("connection_id", sa.String(length=64), nullable=False),
        sa.Column("run_type", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("watermark_before", sa.String(length=128), nullable=True),
        sa.Column("watermark_after", sa.String(length=128), nullable=True),
        sa.Column("records_read", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("records_written", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("records_failed", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["connection_id"], ["connector_connection.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_connector_sync_run_id"), "connector_sync_run", ["id"], unique=False)
    op.create_index(
        op.f("ix_connector_sync_run_connection_id"),
        "connector_sync_run",
        ["connection_id"],
        unique=False,
    )
    op.create_index(op.f("ix_connector_sync_run_org_id"), "connector_sync_run", ["org_id"], unique=False)
    op.create_index(
        "ix_connector_sync_run_connection_started_at",
        "connector_sync_run",
        ["connection_id", "started_at"],
        unique=False,
    )

    op.create_table(
        "connector_sync_checkpoint",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("org_id", sa.String(length=64), nullable=False),
        sa.Column("connection_id", sa.String(length=64), nullable=False),
        sa.Column("entity_name", sa.String(length=64), nullable=False),
        sa.Column("cursor_value", sa.String(length=255), nullable=True),
        sa.Column("cursor_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["connection_id"], ["connector_connection.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("connection_id", "entity_name", name="uq_sync_checkpoint_conn_entity"),
    )
    op.create_index(
        op.f("ix_connector_sync_checkpoint_connection_id"),
        "connector_sync_checkpoint",
        ["connection_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_connector_sync_checkpoint_org_id"),
        "connector_sync_checkpoint",
        ["org_id"],
        unique=False,
    )

    op.create_table(
        "connector_sync_error",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("org_id", sa.String(length=64), nullable=False),
        sa.Column("connection_id", sa.String(length=64), nullable=False),
        sa.Column("sync_run_id", sa.String(length=64), nullable=False),
        sa.Column("entity_name", sa.String(length=64), nullable=True),
        sa.Column("source_object_id", sa.String(length=255), nullable=True),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("error_message", sa.String(length=2000), nullable=False),
        sa.Column("error_payload_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["connection_id"], ["connector_connection.id"]),
        sa.ForeignKeyConstraint(["sync_run_id"], ["connector_sync_run.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_connector_sync_error_connection_id"), "connector_sync_error", ["connection_id"], unique=False)
    op.create_index(op.f("ix_connector_sync_error_sync_run_id"), "connector_sync_error", ["sync_run_id"], unique=False)
    op.create_index(op.f("ix_connector_sync_error_org_id"), "connector_sync_error", ["org_id"], unique=False)

    op.create_table(
        "ods_identity_user",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("org_id", sa.String(length=64), nullable=False),
        sa.Column("connection_id", sa.String(length=64), nullable=False),
        sa.Column("source_object_id", sa.String(length=255), nullable=False),
        sa.Column("distinguished_name", sa.String(length=2048), nullable=True),
        sa.Column("user_principal_name", sa.String(length=255), nullable=True),
        sa.Column("sam_account_name", sa.String(length=255), nullable=True),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("mail", sa.String(length=255), nullable=True),
        sa.Column("department", sa.String(length=255), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("manager_source_object_id", sa.String(length=255), nullable=True),
        sa.Column("account_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("source_created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("raw_payload_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["connection_id"], ["connector_connection.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("connection_id", "source_object_id", name="uq_ods_user_conn_source_object"),
    )
    op.create_index(op.f("ix_ods_identity_user_org_id"), "ods_identity_user", ["org_id"], unique=False)
    op.create_index(op.f("ix_ods_identity_user_connection_id"), "ods_identity_user", ["connection_id"], unique=False)
    op.create_index(op.f("ix_ods_identity_user_source_object_id"), "ods_identity_user", ["source_object_id"], unique=False)

    op.create_table(
        "ods_identity_group",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("org_id", sa.String(length=64), nullable=False),
        sa.Column("connection_id", sa.String(length=64), nullable=False),
        sa.Column("source_object_id", sa.String(length=255), nullable=False),
        sa.Column("distinguished_name", sa.String(length=2048), nullable=True),
        sa.Column("group_name", sa.String(length=255), nullable=True),
        sa.Column("mail", sa.String(length=255), nullable=True),
        sa.Column("group_scope", sa.String(length=64), nullable=True),
        sa.Column("group_category", sa.String(length=64), nullable=True),
        sa.Column("managed_by_source_object_id", sa.String(length=255), nullable=True),
        sa.Column("source_created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("raw_payload_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["connection_id"], ["connector_connection.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("connection_id", "source_object_id", name="uq_ods_group_conn_source_object"),
    )
    op.create_index(op.f("ix_ods_identity_group_org_id"), "ods_identity_group", ["org_id"], unique=False)
    op.create_index(op.f("ix_ods_identity_group_connection_id"), "ods_identity_group", ["connection_id"], unique=False)

    op.create_table(
        "ods_identity_group_membership",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("org_id", sa.String(length=64), nullable=False),
        sa.Column("connection_id", sa.String(length=64), nullable=False),
        sa.Column("group_source_object_id", sa.String(length=255), nullable=False),
        sa.Column("member_source_object_id", sa.String(length=255), nullable=False),
        sa.Column("member_object_class", sa.String(length=64), nullable=True),
        sa.Column("source_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("raw_payload_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["connection_id"], ["connector_connection.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "connection_id",
            "group_source_object_id",
            "member_source_object_id",
            name="uq_ods_group_membership_conn_group_member",
        ),
    )
    op.create_index(
        op.f("ix_ods_identity_group_membership_org_id"),
        "ods_identity_group_membership",
        ["org_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ods_identity_group_membership_connection_id"),
        "ods_identity_group_membership",
        ["connection_id"],
        unique=False,
    )

    op.create_table(
        "ods_identity_ou",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("org_id", sa.String(length=64), nullable=False),
        sa.Column("connection_id", sa.String(length=64), nullable=False),
        sa.Column("source_object_id", sa.String(length=255), nullable=False),
        sa.Column("distinguished_name", sa.String(length=2048), nullable=True),
        sa.Column("ou_name", sa.String(length=255), nullable=True),
        sa.Column("parent_source_object_id", sa.String(length=255), nullable=True),
        sa.Column("source_created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("raw_payload_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["connection_id"], ["connector_connection.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("connection_id", "source_object_id", name="uq_ods_ou_conn_source_object"),
    )
    op.create_index(op.f("ix_ods_identity_ou_org_id"), "ods_identity_ou", ["org_id"], unique=False)
    op.create_index(op.f("ix_ods_identity_ou_connection_id"), "ods_identity_ou", ["connection_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_ods_identity_ou_connection_id"), table_name="ods_identity_ou")
    op.drop_index(op.f("ix_ods_identity_ou_org_id"), table_name="ods_identity_ou")
    op.drop_table("ods_identity_ou")

    op.drop_index(op.f("ix_ods_identity_group_membership_connection_id"), table_name="ods_identity_group_membership")
    op.drop_index(op.f("ix_ods_identity_group_membership_org_id"), table_name="ods_identity_group_membership")
    op.drop_table("ods_identity_group_membership")

    op.drop_index(op.f("ix_ods_identity_group_connection_id"), table_name="ods_identity_group")
    op.drop_index(op.f("ix_ods_identity_group_org_id"), table_name="ods_identity_group")
    op.drop_table("ods_identity_group")

    op.drop_index(op.f("ix_ods_identity_user_source_object_id"), table_name="ods_identity_user")
    op.drop_index(op.f("ix_ods_identity_user_connection_id"), table_name="ods_identity_user")
    op.drop_index(op.f("ix_ods_identity_user_org_id"), table_name="ods_identity_user")
    op.drop_table("ods_identity_user")

    op.drop_index(op.f("ix_connector_sync_error_org_id"), table_name="connector_sync_error")
    op.drop_index(op.f("ix_connector_sync_error_sync_run_id"), table_name="connector_sync_error")
    op.drop_index(op.f("ix_connector_sync_error_connection_id"), table_name="connector_sync_error")
    op.drop_table("connector_sync_error")

    op.drop_index(op.f("ix_connector_sync_checkpoint_org_id"), table_name="connector_sync_checkpoint")
    op.drop_index(op.f("ix_connector_sync_checkpoint_connection_id"), table_name="connector_sync_checkpoint")
    op.drop_table("connector_sync_checkpoint")

    op.drop_index("ix_connector_sync_run_connection_started_at", table_name="connector_sync_run")
    op.drop_index(op.f("ix_connector_sync_run_org_id"), table_name="connector_sync_run")
    op.drop_index(op.f("ix_connector_sync_run_connection_id"), table_name="connector_sync_run")
    op.drop_index(op.f("ix_connector_sync_run_id"), table_name="connector_sync_run")
    op.drop_table("connector_sync_run")

    op.drop_index(op.f("ix_connector_connection_connector_type_id"), table_name="connector_connection")
    op.drop_index(op.f("ix_connector_connection_org_id"), table_name="connector_connection")
    op.drop_index(op.f("ix_connector_connection_id"), table_name="connector_connection")
    op.drop_table("connector_connection")

    op.drop_index(op.f("ix_connector_type_slug"), table_name="connector_type")
    op.drop_index(op.f("ix_connector_type_id"), table_name="connector_type")
    op.drop_table("connector_type")
