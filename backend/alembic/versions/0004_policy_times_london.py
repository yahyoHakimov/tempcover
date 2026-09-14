"""reinterpret stored policy times as Europe/London wall clock

Revision ID: 0004_policy_times_london
Revises: 0003_driver_sex

Ilgari agent kiritgan vaqt UTC deb saqlanardi. Endi parse_dt uni Europe/London
deb qabul qilib UTC ga o'giradi. Mavjud qatorlar ham shunga moslanadi:
saqlangan devor soati London vaqti deb qayta talqin qilinadi.
"""
from alembic import op

revision = "0004_policy_times_london"
down_revision = "0003_driver_sex"
branch_labels = None
depends_on = None

COLS = ("start_datetime", "end_datetime")


def upgrade() -> None:
    for c in COLS:
        # timestamptz -> London devor soati (naive) -> London zonasi bilan timestamptz
        op.execute(f"UPDATE policies SET {c} = ({c} AT TIME ZONE 'UTC') AT TIME ZONE 'Europe/London'")


def downgrade() -> None:
    for c in COLS:
        op.execute(f"UPDATE policies SET {c} = ({c} AT TIME ZONE 'Europe/London') AT TIME ZONE 'UTC'")
