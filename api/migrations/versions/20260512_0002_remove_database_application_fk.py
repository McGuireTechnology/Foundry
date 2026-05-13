"""legacy no-op migration retained for revision continuity

Revision ID: 20260512_0002
Revises: 20260512_0001
Create Date: 2026-05-12 14:40:00.000000
"""

from collections.abc import Sequence

revision: str = "20260512_0002"
down_revision: str | None = "20260512_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None
# Alembic reads these module-level identifiers dynamically.
_ = (revision, down_revision, branch_labels, depends_on)


def upgrade() -> None:
    # The initial migration now creates the canonical database schema directly.
    # This revision remains as a no-op to preserve deployed revision history.
    pass


def downgrade() -> None:
    pass
