"""add alias to users

Revision ID: b7d6c1a2e5f4
Revises: a3f9c81e2b4d
Create Date: 2026-09-20
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b7d6c1a2e5f4'
down_revision: Union[str, Sequence[str], None] = 'a3f9c81e2b4d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # add alias nullable first
    op.add_column('users', sa.Column('alias', sa.String(length=50), nullable=True))
    # backfill alias = username
    op.execute(sa.text("UPDATE users SET alias = username WHERE alias IS NULL"))
    # create unique constraint for alias
    # use batch for sqlite compatibility
    with op.batch_alter_table('users') as batch_op:
        batch_op.create_unique_constraint('uq_users_alias', ['alias'])
        batch_op.alter_column('alias', existing_type=sa.String(length=50), nullable=False)


def downgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_constraint('uq_users_alias', type_='unique')
    op.drop_column('users', 'alias')
