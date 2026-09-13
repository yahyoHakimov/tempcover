"""initial schema

Creates every table from the SQLAlchemy models. Existing tables are left untouched
(create_all uses checkfirst), so this is safe on a database that was bootstrapped earlier.

Revision ID: 0001_initial
Revises:
"""
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    from app.models.models import Base
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    pass
