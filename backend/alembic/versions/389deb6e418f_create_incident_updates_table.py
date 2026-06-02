"""create incident updates table

Revision ID: 389deb6e418f
Revises: 2c01600c28af
Create Date: 2026-06-02 18:40:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '389deb6e418f'
down_revision: Union[str, None] = '2c01600c28af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# status REUSES the existing incident_status enum (created by the incidents
# migration). create_type=False ensures op.create_table references it rather
# than issuing CREATE TYPE. The enum is NOT dropped on downgrade — it is owned
# by the incidents table/migration.
incident_status_enum = postgresql.ENUM(
    'open', 'investigating', 'mitigated', 'resolved',
    name='incident_status', create_type=False,
)


def upgrade() -> None:
    op.create_table(
        'incident_updates',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('incident_id', sa.Uuid(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('author', sa.String(length=255), nullable=True),
        sa.Column('status', incident_status_enum, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_incident_updates_incident_id'), 'incident_updates', ['incident_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_incident_updates_incident_id'), table_name='incident_updates')
    op.drop_table('incident_updates')
    # incident_status enum is shared with the incidents table — do NOT drop it.