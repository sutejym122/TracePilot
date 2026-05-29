"""create releases table

Revision ID: 57902a10e54d
Revises: 2236311ce241
Create Date: 2026-05-29 22:53:45.153664
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '57902a10e54d'
down_revision: Union[str, None] = '2236311ce241'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Use the postgresql dialect ENUM with create_type=False so op.create_table
# references existing types instead of re-issuing CREATE TYPE. 'environment'
# already exists (services migration); 'release_status' is created explicitly
# in upgrade() before the table. On SQLite these render as plain VARCHAR checks.
environment_enum = postgresql.ENUM(
    'dev', 'uat', 'prod', name='environment', create_type=False
)
release_status_enum = postgresql.ENUM(
    'planned', 'in_progress', 'testing', 'released', 'rolled_back',
    name='release_status', create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        # Create only the NEW type; environment already exists.
        bind.execute(sa.text(
            "DO $$ BEGIN "
            "IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'release_status') THEN "
            "CREATE TYPE release_status AS ENUM "
            "('planned','in_progress','testing','released','rolled_back'); "
            "END IF; END $$;"
        ))

    op.create_table(
        'releases',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('service_id', sa.Uuid(), nullable=False),
        sa.Column('version', sa.String(length=255), nullable=False),
        sa.Column('environment', environment_enum, nullable=False),
        sa.Column('status', release_status_enum, nullable=False),
        sa.Column('owner', sa.String(length=255), nullable=True),
        sa.Column('release_notes', sa.Text(), nullable=True),
        sa.Column('released_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_releases_service_id'), 'releases', ['service_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_releases_service_id'), table_name='releases')
    op.drop_table('releases')
    # 'environment' is shared with the services table — do NOT drop it.
    # Only release_status (created by this migration) is removed.
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        bind.execute(sa.text("DROP TYPE IF EXISTS release_status"))