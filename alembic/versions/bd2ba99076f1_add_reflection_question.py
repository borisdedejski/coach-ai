"""Add reflection_question

Revision ID: bd2ba99076f1
Revises: 
Create Date: 2025-07-01 12:47:04.832029

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bd2ba99076f1'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('journal_entries', sa.Column('reflection_question', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('journal_entries', 'reflection_question')
