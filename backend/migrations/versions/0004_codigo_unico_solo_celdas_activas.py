
"""Permite reutilizar códigos de celdas eliminadas.

Revision ID: 0004
Revises: 8cf44f334bc4
"""

from alembic import op
import sqlalchemy as sa


revision = "0004"
down_revision = "8cf44f334bc4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint(
        "uq_celda_codigo",
        "celda",
        type_="unique",
    )

    op.create_index(
        "uq_celda_codigo_activa",
        "celda",
        ["codigo"],
        unique=True,
        postgresql_where=sa.text("eliminada = false"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_celda_codigo_activa",
        table_name="celda",
    )

    op.create_unique_constraint(
        "uq_celda_codigo",
        "celda",
        ["codigo"],
    )
