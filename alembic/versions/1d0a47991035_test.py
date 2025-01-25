"""test

Revision ID: 1d0a47991035
Revises: 
Create Date: 2025-01-14 10:42:01.480460

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d0a47991035'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('todos', sa.Column('note', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("todos", 'note')
