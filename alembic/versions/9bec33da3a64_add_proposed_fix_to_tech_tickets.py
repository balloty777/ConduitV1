"""add proposed fix to tech tickets

Revision ID: 9bec33da3a64
Revises: 352114b403fe
Create Date: 2026-10-06 08:16:07.069342

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9bec33da3a64"
down_revision: Union[str, Sequence[str], None] = "352114b403fe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "tech_tickets",
        sa.Column(
            "proposed_fix",
            sa.Text(),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE tech_tickets
        SET proposed_fix = 'No proposed fix recorded for this ticket.'
        WHERE proposed_fix IS NULL
        """
    )

    op.alter_column(
        "tech_tickets",
        "proposed_fix",
        existing_type=sa.Text(),
        nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column("tech_tickets", "proposed_fix")