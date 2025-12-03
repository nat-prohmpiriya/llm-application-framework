"""add_document_description_and_tags

Revision ID: 655270e1272a
Revises: d5e6f7g8h9i0
Create Date: 2025-12-03 23:40:17.619504

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '655270e1272a'
down_revision: Union[str, None] = 'd5e6f7g8h9i0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add description and tags columns to documents table
    op.add_column('documents', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('documents', sa.Column('tags', postgresql.ARRAY(sa.String(length=50)), nullable=True))


def downgrade() -> None:
    op.drop_column('documents', 'tags')
    op.drop_column('documents', 'description')
