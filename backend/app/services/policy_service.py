"""
Policy service — number generation, lifecycle status, cancellation, and email delivery
shared by the agent and super-admin routers.
"""

import random
import string
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import BackgroundTasks
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.database import SessionLocal
from app.models.models import Policy, PolicyStatus, ReasonForIssue, CoverType
from app.services import email_service

DISPLAY_DT = "%A, %d %B %Y at %-I:%M %p"   # Friday, 11 September 2026 at 9:18 PM


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def generate_policy_number() -> str:
    return f"{settings.POLICY_NUMBER_PREFIX}{''.join(random.choices(string.digits, k=8))}"


def normalise_policy_number(raw: str) -> str:
    """Accept 'tcv-mot-12345678', '12345678' or 'TCV MOT 12345678' and return the stored form."""
    s = (raw or "").strip().upper().replace(" ", "")
    prefix = settings.POLICY_NUMBER_PREFIX.upper()
    if s.isdigit() and len(s) == 8:
        return f"{prefix}{s}"
    if prefix and not s.startswith(prefix):
        compact = prefix.replace("-", "")
        if s.startswith(compact):
            return f"{prefix}{s[len(compact):]}"
    return s


def parse_dt(value: str) -> datetime:
    """Policy times are entered as wall-clock values without a zone; they are stored as UTC."""
    dt = datetime.fromisoformat(value)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def status_for(start: datetime, end: datetime, now: Optional[datetime] = None) -> PolicyStatus:
    now = now or utcnow()
    if end <= now:
        return PolicyStatus.EXPIRED
    if start > now:
        return PolicyStatus.PENDING
    return PolicyStatus.ACTIVE


def fmt_email(dt: datetime) -> str:
    return dt.strftime(email_service.EMAIL_DT) if dt else ""


def fmt_display(dt: datetime) -> str:
    return dt.strftime(DISPLAY_DT) if dt else ""


# ─────────────────────────────────────────────────────────────────────────────

def create_policy(
    db: Session, *, tenant_id, driver_id, vehicle_id,
    start: datetime, end: datetime, price: float, cover_type: CoverType,
) -> Policy:
    if end <= start:
        raise ValueError("End must be after start")

    for _ in range(10):
        policy = Policy(
            tenant_id=tenant_id,
            driver_id=driver_id,
            vehicle_id=vehicle_id,
            policy_number=generate_policy_number(),
            start_datetime=start,
            end_datetime=end,
            price=price,
            cover_type=cover_type,
            status=status_for(start, end),
            verify_token=uuid.uuid4().hex[:32],
            email_sent=False,
            version=1,
        )
        db.add(policy)
        try:
            db.commit()
            db.refresh(policy)
            return policy
        except IntegrityError:
            db.rollback()
    raise RuntimeError("Could not generate a unique policy number")


def apply_update(policy: Policy, *, start=None, end=None, price=None, cover_type=None) -> bool:
    """Apply a mid-term adjustment. Returns True when something material changed
    (version bumped, reason set to MTA, status recomputed)."""
    changed = False
    if start is not None and start != policy.start_datetime:
        policy.start_datetime = start; changed = True
    if end is not None and end != policy.end_datetime:
        policy.end_datetime = end; changed = True
    if price is not None and float(price) != float(policy.price):
        policy.price = price; changed = True
    if cover_type is not None and cover_type != policy.cover_type:
        policy.cover_type = cover_type; changed = True

    if changed:
        if policy.end_datetime <= policy.start_datetime:
            raise ValueError("End must be after start")
        policy.version = (policy.version or 1) + 1
        policy.reason_for_issue = ReasonForIssue.MTA
        if policy.status in (PolicyStatus.ACTIVE, PolicyStatus.PENDING):
            policy.status = status_for(policy.start_datetime, policy.end_datetime)
    return changed


def cancel(db: Session, policy: Policy, reason: Optional[str], background_tasks: BackgroundTasks) -> bool:
    """Cancel a policy and notify the driver. Returns False if it was already cancelled."""
    if policy.status == PolicyStatus.CANCELLED:
        return False
    policy.status = PolicyStatus.CANCELLED
    policy.cancelled_at = utcnow()
    policy.cancellation_reason = (reason or "").strip()[:255] or None
    db.commit()

    driver = policy.driver
    if driver and driver.email:
        background_tasks.add_task(
            email_service.send_policy_cancellation_email,
            to_email=driver.email,
            driver_name=f"{driver.first_name} {driver.last_name}",
            policy_number=policy.policy_number,
            reason=policy.cancellation_reason,
        )
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Email delivery (background)
# ─────────────────────────────────────────────────────────────────────────────

def queue_policy_email(background_tasks: BackgroundTasks, policy_id, kind: str = "confirmation") -> None:
    background_tasks.add_task(deliver_policy_email, str(policy_id), kind)


def deliver_policy_email(policy_id: str, kind: str = "confirmation") -> str:
    """Runs in the background with its own session. kind: 'confirmation' | 'updated'."""
    db = SessionLocal()
    try:
        policy = (
            db.query(Policy)
            .options(joinedload(Policy.driver), joinedload(Policy.vehicle))
            .filter(Policy.id == policy_id)
            .first()
        )
        if not policy or not policy.driver or not policy.vehicle:
            return "failed"
        d, v = policy.driver, policy.vehicle
        result = email_service.send_policy_confirmation_email(
            to_email=d.email,
            driver_name=f"{d.first_name} {d.last_name}",
            policy_number=policy.policy_number,
            start_datetime=fmt_email(policy.start_datetime),
            end_datetime=fmt_email(policy.end_datetime),
            vehicle_reg=v.registration,
            vehicle_make_model=f"{v.make} {v.model}",
            price=str(policy.price),
            verify_token=policy.verify_token,
            updated=(kind == "updated"),
            version=policy.version or 1,
        )
        if result == "sent":
            policy.email_sent = True
            policy.email_sent_at = utcnow()
            db.commit()
        return result
    finally:
        db.close()
