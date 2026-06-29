"""add agents entity + agent_id on clients and client_invoices

Revision ID: b2d7e4f9a1c3
Revises: c1a551a580e0
Create Date: 2026-06-29 10:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b2d7e4f9a1c3'
down_revision: Union[str, None] = 'c1a551a580e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'agents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('business_name', sa.String(length=200), nullable=False),
        sa.Column('legal_name', sa.String(length=200), nullable=True),
        sa.Column('contact_person', sa.String(length=120), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=40), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('gst_number', sa.String(length=30), nullable=True),
        sa.Column('pan', sa.String(length=20), nullable=True),
        sa.Column('bank_account_holder', sa.String(length=160), nullable=True),
        sa.Column('bank_name', sa.String(length=160), nullable=True),
        sa.Column('account_number', sa.String(length=40), nullable=True),
        sa.Column('ifsc_code', sa.String(length=20), nullable=True),
        sa.Column('commission_rate', sa.Float(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_agents_business_name'), 'agents', ['business_name'], unique=False)

    op.add_column('clients', sa.Column('agent_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_clients_agent_id', 'clients', 'agents', ['agent_id'], ['id'], ondelete='SET NULL'
    )

    op.add_column('client_invoices', sa.Column('agent_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_client_invoices_agent_id', 'client_invoices', 'agents', ['agent_id'], ['id'], ondelete='SET NULL'
    )


def downgrade() -> None:
    op.drop_constraint('fk_client_invoices_agent_id', 'client_invoices', type_='foreignkey')
    op.drop_column('client_invoices', 'agent_id')

    op.drop_constraint('fk_clients_agent_id', 'clients', type_='foreignkey')
    op.drop_column('clients', 'agent_id')

    op.drop_index(op.f('ix_agents_business_name'), table_name='agents')
    op.drop_table('agents')
