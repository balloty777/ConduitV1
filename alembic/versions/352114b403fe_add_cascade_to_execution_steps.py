"""add cascade to execution steps

Revision ID: 352114b403fe

Revises: 8b2914dfcbbb

Create Date: 2026-09-27 14:55:04.299567

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "352114b403fe"
down_revision: Union[str, Sequence[str], None] = "8b2914dfcbbb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.drop_constraint(
        "execution_steps_execution_id_fkey",
        "execution_steps",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "execution_steps_execution_id_fkey",
        "execution_steps",
        "workflow_executions",
        ["execution_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "execution_steps_execution_id_fkey",
        "execution_steps",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "execution_steps_execution_id_fkey",
        "execution_steps",
        "workflow_executions",
        ["execution_id"],
        ["id"],
    )