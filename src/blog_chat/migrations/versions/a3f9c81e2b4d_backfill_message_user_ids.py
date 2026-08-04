"""backfill message user_id

Revision ID: a3f9c81e2b4d
Revises: a2cfa0d6c02a
Create Date: 2026-08-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a3f9c81e2b4d'
down_revision: Union[str, Sequence[str], None] = 'a2cfa0d6c02a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Backfill user_id on existing messages from the matching username."""
    op.execute(
        """
        UPDATE messages
        SET user_id = (SELECT users.id FROM users WHERE users.username = messages.username)
        WHERE user_id IS NULL
        """
    )


def downgrade() -> None:
    """Data backfill is not reversible."""
    pass
