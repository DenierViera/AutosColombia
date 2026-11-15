"""unifica ramas de migraciones

Revision ID: 8cf44f334bc4
Revises: 0003, c76703487f68
"""
from alembic import op
import sqlalchemy as sa


revision = '8cf44f334bc4'
down_revision = ('0003', 'c76703487f68')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
