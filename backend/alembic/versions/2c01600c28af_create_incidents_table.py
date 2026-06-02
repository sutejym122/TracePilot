"""create incidents table

Revision ID: 2c01600c28af
Revises: ce7a50a7ff28
Create Date: 2026-06-02 18:10:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '2c01600c28af'
down_revision: Union[str, None] = 'ce7a50a7ff28'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Two NEW enums. Create them explicitly (idempotently) before the table and
# reference them with create_type=False so op.create_table doesn't re-issue
# CREATE TYPE. On SQLite these render as plain VARCHAR checks.
incident_severity_enum = postgresql.ENUM(
    'low', 'medium', 'high', 'critical', name='incident_severity', create_type=False
)
incident_status_enum = postgresql.ENUM(
    'open', 'investigating', 'mitigated', 'resolved', name='incident_status', create_type=False
)


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        bind.execute(sa.text(
            "DO $$ BEGIN "
            "IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'incident_severity') THEN "
            "CREATE TYPE incident_severity AS ENUM ('low','medium','high','critical'); "
            "END IF; END $$;"
        ))
        bind.execute(sa.text(
            "DO $$ BEGIN "
            "IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'incident_status') THEN "
            "CREATE TYPE incident_status AS ENUM ('open','investigating','mitigated','resolved'); "
            "END IF; END $$;"
        ))

    op.create_table(
        'incidents',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('service_id', sa.Uuid(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('severity', incident_severity_enum, nullable=False),
        sa.Column('status', incident_status_enum, nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('root_cause', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_incidents_service_id'), 'incidents', ['service_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_incidents_service_id'), table_name='incidents')
    op.drop_table('incidents')
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        bind.execute(sa.text("DROP TYPE IF EXISTS incident_status"))
        bind.execute(sa.text("DROP TYPE IF EXISTS incident_severity"))