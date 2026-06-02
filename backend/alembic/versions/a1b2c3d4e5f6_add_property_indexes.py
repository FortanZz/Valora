"""add property indexes

Revision ID: a1b2c3d4e5f6
Revises: 49093c121816
Create Date: 2026-06-02 14:20:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "49093c121816"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("ix_properties_price", "properties", ["price"], unique=False)
    op.create_index("ix_properties_location", "properties", ["location"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_properties_location", table_name="properties")
    op.drop_index("ix_properties_price", table_name="properties")
