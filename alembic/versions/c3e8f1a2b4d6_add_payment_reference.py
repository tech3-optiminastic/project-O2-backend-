"""add payment_reference to payment_approvals

Revision ID: c3e8f1a2b4d6
Revises: b2d7e4f9a1c3
Create Date: 2026-06-29 13:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c3e8f1a2b4d6'
down_revision: Union[str, None] = 'b2d7e4f9a1c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('payment_approvals', sa.Column('payment_reference', sa.String(length=120), nullable=True))


def downgrade() -> None:
    op.drop_column('payment_approvals', 'payment_reference')
