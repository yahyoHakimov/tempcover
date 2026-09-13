"""
Policy lifecycle jobs — run every LIFECYCLE_TICK_SECONDS from the app's background loop.

  1. pending  -> active   when the start time is reached
  2. active   -> expired  when the end time has passed
  3. driver reminder      REMINDER_HOURS_BEFORE_EXPIRY before the end (once per policy)
  4. agent digest         once a day at AGENT_DIGEST_HOUR_UTC: policies ending in the next N days

All steps are idempotent, so running more than one instance only costs duplicate work, not duplicate emails
(the reminder and digest are flagged on the row before the tick commits).
"""

from datetime import timedelta

from sqlalchemy.orm import joinedload

from app.config import settings
from app.database import SessionLocal
from app.models.models import Policy, PolicyStatus, Tenant, TenantStatus, Driver, Vehicle
from app.services import email_service
from app.services.policy_service import utcnow, fmt_display


def tick() -> dict:
    db = SessionLocal()
    stats = {"activated": 0, "expired": 0, "reminders": 0, "digests": 0}
    try:
        now = utcnow()

        # 1 + 2: status transitions
        stats["activated"] = (
            db.query(Policy)
            .filter(Policy.status == PolicyStatus.PENDING, Policy.start_datetime <= now, Policy.end_datetime > now)
            .update({Policy.status: PolicyStatus.ACTIVE}, synchronize_session=False)
        )
        stats["expired"] = (
            db.query(Policy)
            .filter(Policy.status.in_([PolicyStatus.ACTIVE, PolicyStatus.PENDING]), Policy.end_datetime <= now)
            .update({Policy.status: PolicyStatus.EXPIRED}, synchronize_session=False)
        )
        db.commit()

        # 3: driver reminders
        if settings.REMINDER_HOURS_BEFORE_EXPIRY > 0:
            window = now + timedelta(hours=settings.REMINDER_HOURS_BEFORE_EXPIRY)
            due = (
                db.query(Policy)
                .options(joinedload(Policy.driver), joinedload(Policy.vehicle))
                .filter(
                    Policy.status == PolicyStatus.ACTIVE,
                    Policy.end_datetime > now,
                    Policy.end_datetime <= window,
                    Policy.expiry_reminder_sent_at.is_(None),
                )
                .all()
            )
            for p in due:
                p.expiry_reminder_sent_at = now          # flag first so a crash mid-send cannot repeat it forever
                db.commit()
                if p.driver and p.driver.email:
                    email_service.send_expiry_reminder_email(
                        to_email=p.driver.email,
                        driver_name=f"{p.driver.first_name} {p.driver.last_name}",
                        policy_number=p.policy_number,
                        vehicle_reg=p.vehicle.registration if p.vehicle else "",
                        end_display=fmt_display(p.end_datetime),
                        verify_token=p.verify_token,
                    )
                    stats["reminders"] += 1

        # 4: agent digest
        if settings.AGENT_DIGEST_DAYS_AHEAD > 0 and now.hour == settings.AGENT_DIGEST_HOUR_UTC:
            today = now.date()
            horizon = now + timedelta(days=settings.AGENT_DIGEST_DAYS_AHEAD)
            tenants = (
                db.query(Tenant)
                .filter(Tenant.status == TenantStatus.ACTIVE, Tenant.email.isnot(None))
                .filter((Tenant.expiry_digest_sent_on.is_(None)) | (Tenant.expiry_digest_sent_on < today))
                .all()
            )
            for t in tenants:
                t.expiry_digest_sent_on = today
                db.commit()
                rows = (
                    db.query(Policy, Driver, Vehicle)
                    .join(Driver, Policy.driver_id == Driver.id)
                    .join(Vehicle, Policy.vehicle_id == Vehicle.id)
                    .filter(Policy.tenant_id == t.id, Policy.status == PolicyStatus.ACTIVE,
                            Policy.end_datetime > now, Policy.end_datetime <= horizon)
                    .order_by(Policy.end_datetime)
                    .all()
                )
                if not rows:
                    continue
                email_service.send_agent_expiry_digest_email(
                    to_email=t.email,
                    agent_name=t.name,
                    rows=[{
                        "policy_number": p.policy_number,
                        "driver_name":   f"{d.first_name} {d.last_name}",
                        "vehicle_reg":   v.registration,
                        "end_display":   fmt_display(p.end_datetime),
                    } for p, d, v in rows],
                    days_ahead=settings.AGENT_DIGEST_DAYS_AHEAD,
                )
                stats["digests"] += 1
        return stats
    finally:
        db.close()
