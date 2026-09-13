"""policy lifecycle columns: version, cancellation, expiry reminders, agent digest

Revision ID: 0002_policy_lifecycle
Revises: 0001_initial
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_policy_lifecycle"
down_revision = "0001_initial"
branch_labels = None
depends_on = None

COLUMNS = [
    ("policies", "version",                 sa.Integer(),                 dict(nullable=False, server_default="1")),
    ("policies", "cancelled_at",            sa.DateTime(timezone=True),   dict(nullable=True)),
    ("policies", "cancellation_reason",     sa.String(255),               dict(nullable=True)),
    ("policies", "expiry_reminder_sent_at", sa.DateTime(timezone=True),   dict(nullable=True)),
    ("tenants",  "expiry_digest_sent_on",   sa.Date(),                    dict(nullable=True)),
]


def _existing(bind, table):
    return {c["name"] for c in sa.inspect(bind).get_columns(table)}


def upgrade() -> None:
    bind = op.get_bind()
    for table, name, type_, kw in COLUMNS:
        if name not in _existing(bind, table):
            op.add_column(table, sa.Column(name, type_, **kw))


def downgrade() -> None:
    bind = op.get_bind()
    for table, name, _, _ in reversed(COLUMNS):
        if name in _existing(bind, table):
            op.drop_column(table, name)
