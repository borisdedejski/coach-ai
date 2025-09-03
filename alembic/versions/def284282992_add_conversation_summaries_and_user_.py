"""add_conversation_summaries_and_user_memory

Revision ID: def284282992
Revises: bd2ba99076f1
Create Date: 2025-09-02 13:23:24.563084

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'def284282992'
down_revision: Union[str, Sequence[str], None] = 'bd2ba99076f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
