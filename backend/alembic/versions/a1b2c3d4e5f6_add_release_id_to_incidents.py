"""add release_id to incidents

Revision ID: a1b2c3d4e5f6
Revises: 054d734864fa
Create Date: 2026-06-05 04:10:00.000000

Adds an optional incident -> release link. Nullable FK with ON DELETE SET NULL
so deleting a release clears the link rather than cascading the delete to
incidents. No enum types involved (plain UUID FK), so no CREATE/DROP TYPE.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '054d734864fa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "incidents",
        sa.Column("release_id", sa.Uuid(), nullable=True),
    )
    op.create_index(
        op.f("ix_incidents_release_id"), "incidents", ["release_id"], unique=False
    )
    op.create_foreign_key(
        "fk_incidents_release_id_releases",
        "incidents",
        "releases",
        ["release_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_incidents_release_id_releases", "incidents", type_="foreignkey"
    )
    op.drop_index(op.f("ix_incidents_release_id"), table_name="incidents")
    op.drop_column("incidents", "release_id")