"""policy usage (leisure / business) — drives the certificate's Limitations to use

Revision ID: 0005_policy_usage
Revises: 0004_policy_times_london
"""
from alembic import op
import sqlalchemy as sa

revision = "0005_policy_usage"
down_revision = "0004_policy_times_london"
branch_labels = None
depends_on = None


def _existing(bind, table):
    return {c["name"] for c in sa.inspect(bind).get_columns(table)}


def upgrade() -> None:
    # Mavjud polislar "leisure" bo'lib qoladi — sertifikat matni o'zgarmaydi
    if "usage" not in _existing(op.get_bind(), "policies"):
        op.add_column("policies", sa.Column("usage", sa.String(20), nullable=False, server_default="leisure"))


def downgrade() -> None:
    if "usage" in _existing(op.get_bind(), "policies"):
        op.drop_column("policies", "usage")
