"""
Policies Router — agent scope (every query is isolated to the signed-in tenant)
"""

from typing import List, Optional
from uuid import UUID
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.models.models import Policy, Driver, Vehicle, PolicyStatus, CoverType
from app.services import policy_service as ps
from app.services.branding import cover_label

router = APIRouter()


def fmt_dt(dt) -> str:
    if dt is None:
        return ""
    return dt.isoformat() if hasattr(dt, "isoformat") else str(dt)


# ── Schemas ──────────────────────────────────────────────────────────────────

class PolicyCreate(BaseModel):
    driver_id: UUID
    vehicle_id: UUID
    start_datetime: str
    end_datetime: str
    price: float
    cover_type: CoverType = CoverType.FULLY_COMPREHENSIVE


class PolicyUpdate(BaseModel):
    start_datetime: Optional[str] = None
    end_datetime: Optional[str] = None
    price: Optional[float] = None
    cover_type: Optional[CoverType] = None


class PolicyCancel(BaseModel):
    reason: Optional[str] = None


class PolicyResponse(BaseModel):
    id: UUID
    policy_number: str
    driver_id: UUID
    vehicle_id: UUID
    start_datetime: str
    end_datetime: str
    price: float
    cover_type: str
    status: str
    email_sent: bool
    issued_at: str
    version: int = 1
    cancelled_at: Optional[str] = None
    cancellation_reason: Optional[str] = None

    class Config:
        from_attributes = True


def to_response(p: Policy) -> PolicyResponse:
    return PolicyResponse(
        id=p.id,
        policy_number=p.policy_number,
        driver_id=p.driver_id,
        vehicle_id=p.vehicle_id,
        start_datetime=fmt_dt(p.start_datetime),
        end_datetime=fmt_dt(p.end_datetime),
        price=float(p.price),
        cover_type=p.cover_type,
        status=p.status,
        email_sent=p.email_sent,
        issued_at=fmt_dt(p.issued_at),
        version=p.version or 1,
        cancelled_at=fmt_dt(p.cancelled_at) or None,
        cancellation_reason=p.cancellation_reason,
    )


def _sync_statuses(db: Session, policies: list) -> None:
    """Lazy safety net for pending→active / →expired between background ticks."""
    now = ps.utcnow()
    dirty = False
    for p in policies:
        if p.status in (PolicyStatus.ACTIVE, PolicyStatus.PENDING) and p.start_datetime and p.end_datetime:
            new = ps.status_for(p.start_datetime, p.end_datetime, now)
            if new != p.status:
                p.status = new
                dirty = True
    if dirty:
        db.commit()


def _get_tenant_policy(db: Session, policy_id: UUID, tenant) -> Policy:
    policy = db.query(Policy).filter(Policy.id == policy_id, Policy.tenant_id == tenant.id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


def _parse_dt(value: str):
    try:
        return ps.parse_dt(value)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid date/time format")


# ── GET all policies ─────────────────────────────────────────────────────────

@router.get("/", response_model=List[PolicyResponse])
def get_policies(
    filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    tenant = current_user["user"]
    query = db.query(Policy).filter(Policy.tenant_id == tenant.id)
    now = ps.utcnow()

    if filter in ("expiring3", "expiringweek"):
        days = 3 if filter == "expiring3" else 7
        query = query.filter(
            Policy.end_datetime <= now + timedelta(days=days),
            Policy.end_datetime >= now,
            Policy.status == PolicyStatus.ACTIVE,
        )

    policies = query.order_by(Policy.issued_at.desc()).all()
    _sync_statuses(db, policies)
    return [to_response(p) for p in policies]


# ── POST create policy ───────────────────────────────────────────────────────

@router.post("/", response_model=PolicyResponse)
def create_policy(
    data: PolicyCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    tenant = current_user["user"]

    driver = db.query(Driver).filter(Driver.id == data.driver_id, Driver.tenant_id == tenant.id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    vehicle = db.query(Vehicle).filter(Vehicle.id == data.vehicle_id, Vehicle.tenant_id == tenant.id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    start, end = _parse_dt(data.start_datetime), _parse_dt(data.end_datetime)
    try:
        policy = ps.create_policy(
            db, tenant_id=tenant.id, driver_id=driver.id, vehicle_id=vehicle.id,
            start=start, end=end, price=data.price, cover_type=data.cover_type,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    ps.queue_policy_email(background_tasks, policy.id, "confirmation")
    return to_response(policy)


# ── GET single policy ────────────────────────────────────────────────────────

@router.get("/{policy_id}")
def get_policy(
    policy_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    tenant = current_user["user"]
    policy = _get_tenant_policy(db, policy_id, tenant)
    _sync_statuses(db, [policy])

    driver  = db.query(Driver).filter(Driver.id == policy.driver_id, Driver.tenant_id == tenant.id).first()
    vehicle = db.query(Vehicle).filter(Vehicle.id == policy.vehicle_id, Vehicle.tenant_id == tenant.id).first()

    return {
        "policy": {
            "id":                  str(policy.id),
            "policy_number":       policy.policy_number,
            "driver_id":           str(policy.driver_id),
            "vehicle_id":          str(policy.vehicle_id),
            "start_datetime":      fmt_dt(policy.start_datetime),
            "end_datetime":        fmt_dt(policy.end_datetime),
            "price":               float(policy.price),
            "cover_type":          policy.cover_type,
            "cover_label":         cover_label(policy.cover_type),
            "status":              policy.status,
            "email_sent":          policy.email_sent,
            "email_sent_at":       fmt_dt(policy.email_sent_at),
            "issued_at":           fmt_dt(policy.issued_at),
            "version":             policy.version or 1,
            "reason_for_issue":    policy.reason_for_issue.value if hasattr(policy.reason_for_issue, "value") else str(policy.reason_for_issue),
            "cancelled_at":        fmt_dt(policy.cancelled_at) or None,
            "cancellation_reason": policy.cancellation_reason,
        },
        "driver": {
            "id":              str(driver.id),
            "first_name":      driver.first_name,
            "last_name":       driver.last_name,
            "date_of_birth":   driver.date_of_birth.strftime("%Y-%m-%d") if driver.date_of_birth else "",
            "driving_licence": driver.driving_licence,
            "email":           driver.email,
            "mobile":          driver.mobile,
            "address_line_1":  driver.address_line_1,
            "address_line_2":  driver.address_line_2 or "",
            "city":            driver.city,
            "postcode":        driver.postcode,
            "occupation":      driver.occupation,
            "sex":             driver.sex or "",
        } if driver else None,
        "vehicle": {
            "id":           str(vehicle.id),
            "registration": vehicle.registration,
            "make":         vehicle.make,
            "model":        vehicle.model,
            "year":         vehicle.year,
            "color":        vehicle.color or "",
            "value_range":  vehicle.value_range.value if hasattr(vehicle.value_range, "value") else str(vehicle.value_range),
        } if vehicle else None,
    }


# ── PATCH update policy (mid-term adjustment) ────────────────────────────────

@router.patch("/{policy_id}", response_model=PolicyResponse)
def update_policy(
    policy_id: UUID,
    data: PolicyUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    tenant = current_user["user"]
    policy = _get_tenant_policy(db, policy_id, tenant)
    _sync_statuses(db, [policy])

    if policy.status == PolicyStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Cannot edit a cancelled policy")
    if policy.status == PolicyStatus.EXPIRED:
        raise HTTPException(status_code=400, detail="Cannot edit an expired policy — issue a new one instead")

    try:
        changed = ps.apply_update(
            policy,
            start=_parse_dt(data.start_datetime) if data.start_datetime is not None else None,
            end=_parse_dt(data.end_datetime) if data.end_datetime is not None else None,
            price=data.price,
            cover_type=data.cover_type,
        )
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    if changed:
        policy.email_sent = False           # documents changed → the driver must get the new set
        db.commit()
        db.refresh(policy)
        ps.queue_policy_email(background_tasks, policy.id, "updated")
    return to_response(policy)


# ── Cancel ───────────────────────────────────────────────────────────────────

@router.post("/{policy_id}/cancel", response_model=PolicyResponse)
def cancel_policy(
    policy_id: UUID,
    data: PolicyCancel,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    tenant = current_user["user"]
    policy = _get_tenant_policy(db, policy_id, tenant)
    ps.cancel(db, policy, data.reason, background_tasks)
    db.refresh(policy)
    return to_response(policy)


@router.delete("/{policy_id}")
def cancel_policy_legacy(
    policy_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """Kept for older clients — same as POST /{id}/cancel without a reason."""
    tenant = current_user["user"]
    policy = _get_tenant_policy(db, policy_id, tenant)
    ps.cancel(db, policy, None, background_tasks)
    return {"message": "Policy cancelled"}


# ── Resend documents email ───────────────────────────────────────────────────

@router.post("/{policy_id}/resend-email")
def resend_email(
    policy_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    tenant = current_user["user"]
    policy = _get_tenant_policy(db, policy_id, tenant)
    if policy.status == PolicyStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="This policy is cancelled")
    ps.queue_policy_email(background_tasks, policy.id, "updated" if (policy.version or 1) > 1 else "confirmation")
    return {"message": "Email queued for sending"}
