"""driver sex column (shown on the Statement of Fact)

Revision ID: 0003_driver_sex
Revises: 0002_policy_lifecycle
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_driver_sex"
down_revision = "0002_policy_lifecycle"
branch_labels = None
depends_on = None


def _existing(bind, table):
    return {c["name"] for c in sa.inspect(bind).get_columns(table)}


def upgrade() -> None:
    if "sex" not in _existing(op.get_bind(), "drivers"):
        op.add_column("drivers", sa.Column("sex", sa.String(10), nullable=True))


def downgrade() -> None:
    if "sex" in _existing(op.get_bind(), "drivers"):
        op.drop_column("drivers", "sex")
