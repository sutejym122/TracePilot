"""create release checklists table

Revision ID: ce7a50a7ff28
Revises: 57902a10e54d
Create Date: 2026-06-02 17:40:18.120397
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'ce7a50a7ff28'
down_revision: Union[str, None] = '57902a10e54d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# readiness_status is a NEW enum. Create it explicitly (idempotently) before the
# table, and reference it with create_type=False so op.create_table doesn't
# re-issue CREATE TYPE. On SQLite this renders as a plain VARCHAR check.
readiness_status_enum = postgresql.ENUM(
    'blocked', 'risky', 'ready', name='readiness_status', create_type=False
)


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        bind.execute(sa.text(
            "DO $$ BEGIN "
            "IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'readiness_status') THEN "
            "CREATE TYPE readiness_status AS ENUM ('blocked','risky','ready'); "
            "END IF; END $$;"
        ))

    op.create_table(
        'release_checklists',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('release_id', sa.Uuid(), nullable=False),
        sa.Column('tests_passed', sa.Boolean(), nullable=False),
        sa.Column('security_review_done', sa.Boolean(), nullable=False),
        sa.Column('rollback_plan_ready', sa.Boolean(), nullable=False),
        sa.Column('monitoring_ready', sa.Boolean(), nullable=False),
        sa.Column('stakeholder_approval', sa.Boolean(), nullable=False),
        sa.Column('readiness_score', sa.Integer(), nullable=False),
        sa.Column('readiness_status', readiness_status_enum, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['release_id'], ['releases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('release_id'),
    )


def downgrade() -> None:
    op.drop_table('release_checklists')
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        bind.execute(sa.text("DROP TYPE IF EXISTS readiness_status"))