"""
Policies Router
"""

import uuid
import random
import string
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.dependencies import require_admin
from app.models.models import Policy, Driver, Vehicle, PolicyStatus, CoverType
from app.services.email_service import send_policy_confirmation_email, send_policy_cancellation_email
from app.config import settings

router = APIRouter()


def generate_policy_number() -> str:
    digits = ''.join(random.choices(string.digits, k=8))
    return digits


def fmt_dt(dt) -> str:
    if dt is None:
        return ""
    if hasattr(dt, 'isoformat'):
        return dt.isoformat()
    return str(dt)


def fmt_dt_display(dt) -> str:
    if dt is None:
        return ""
    if hasattr(dt, 'strftime'):
        return dt.strftime("%d %B %Y at %H:%M")
    return str(dt)


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

    class Config:
        from_attributes = True


# ── GET all policies ──────────────────────────────────────────────────────────

@router.get("/", response_model=List[PolicyResponse])
def get_policies(
    filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    tenant = current_user["user"]
    query = db.query(Policy).filter(Policy.tenant_id == tenant.id)
    now = datetime.now(timezone.utc)

    if filter == "expiring3":
        from datetime import timedelta
        query = query.filter(
            Policy.end_datetime <= now + timedelta(days=3),
            Policy.end_datetime >= now,
            Policy.status == PolicyStatus.ACTIVE,
        )
    elif filter == "expiringweek":
        from datetime import timedelta
        query = query.filter(
            Policy.end_datetime <= now + timedelta(days=7),
            Policy.end_datetime >= now,
            Policy.status == PolicyStatus.ACTIVE,
        )

    policies = query.order_by(Policy.issued_at.desc()).all()

    # Auto-expire policies
    for p in policies:
        if p.status == PolicyStatus.ACTIVE and p.end_datetime and p.end_datetime < now:
            p.status = PolicyStatus.EXPIRED
    db.commit()

    return [
        PolicyResponse(
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
        )
        for p in policies
    ]


# ── POST create policy ────────────────────────────────────────────────────────

@router.post("/", response_model=PolicyResponse)
def create_policy(
    data: PolicyCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    tenant = current_user["user"]

    driver = db.query(Driver).filter(
        Driver.id == data.driver_id,
        Driver.tenant_id == tenant.id,
    ).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    vehicle = db.query(Vehicle).filter(
        Vehicle.id == data.vehicle_id,
        Vehicle.tenant_id == tenant.id,
    ).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    policy_number = generate_policy_number()
    verify_token = str(uuid.uuid4()).replace('-', '')[:32]

    policy = None
    for _ in range(10):
        policy = Policy(
            tenant_id=tenant.id,
            driver_id=data.driver_id,
            vehicle_id=data.vehicle_id,
            policy_number=policy_number,
            start_datetime=datetime.fromisoformat(data.start_datetime),
            end_datetime=datetime.fromisoformat(data.end_datetime),
            price=data.price,
            cover_type=data.cover_type,
            status=PolicyStatus.ACTIVE,
            verify_token=verify_token,
            email_sent=False,
        )
        db.add(policy)
        try:
            db.commit()
            db.refresh(policy)
            break
        except IntegrityError:
            db.rollback()
            policy = None
    else:
        raise HTTPException(status_code=500, detail="Could not generate unique policy number")

    # db_url yo'q — settings.DATABASE_URL ishlatiladi
    background_tasks.add_task(
        _send_confirmation_email,
        policy_id=str(policy.id),
        to_email=driver.email,
        driver_name=f"{driver.first_name} {driver.last_name}",
        policy_number=policy.policy_number,
        start_datetime=fmt_dt_display(policy.start_datetime),
        end_datetime=fmt_dt_display(policy.end_datetime),
        vehicle_reg=vehicle.registration,
        vehicle_make_model=f"{vehicle.make} {vehicle.model}",
        price=str(policy.price),
        verify_token=policy.verify_token,
    )

    return PolicyResponse(
        id=policy.id,
        policy_number=policy.policy_number,
        driver_id=policy.driver_id,
        vehicle_id=policy.vehicle_id,
        start_datetime=fmt_dt(policy.start_datetime),
        end_datetime=fmt_dt(policy.end_datetime),
        price=float(policy.price),
        cover_type=policy.cover_type,
        status=policy.status,
        email_sent=policy.email_sent,
        issued_at=fmt_dt(policy.issued_at),
    )


def _send_confirmation_email(
    policy_id: str,
    to_email: str,
    driver_name: str,
    policy_number: str,
    start_datetime: str,
    end_datetime: str,
    vehicle_reg: str,
    vehicle_make_model: str,
    price: str,
    verify_token: str,
):
    """
    Background task — email yuboradi va email_sent ni yangilaydi.
    settings.DATABASE_URL dan to'g'ridan-to'g'ri ulanadi.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.models.models import Policy as PolicyModel

    # ← db_url parametri yo'q, settings dan olamiz
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        success = send_policy_confirmation_email(
            to_email=to_email,
            driver_name=driver_name,
            policy_number=policy_number,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            vehicle_reg=vehicle_reg,
            vehicle_make_model=vehicle_make_model,
            price=price,
            verify_token=verify_token,
        )

        if success:
            p = db.query(PolicyModel).filter(PolicyModel.id == policy_id).first()
            if p:
                p.email_sent = True
                p.email_sent_at = datetime.now(timezone.utc)
                db.commit()
    finally:
        db.close()


# ── GET single policy ─────────────────────────────────────────────────────────

@router.get("/{policy_id}")
def get_policy(
    policy_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    tenant = current_user["user"]

    policy = db.query(Policy).filter(
        Policy.id == policy_id,
        Policy.tenant_id == tenant.id,
    ).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    driver = db.query(Driver).filter(
        Driver.id == policy.driver_id,
        Driver.tenant_id == tenant.id,
    ).first()

    vehicle = db.query(Vehicle).filter(
        Vehicle.id == policy.vehicle_id,
        Vehicle.tenant_id == tenant.id,
    ).first()

    return {
        "policy": {
            "id":             str(policy.id),
            "policy_number":  policy.policy_number,
            "driver_id":      str(policy.driver_id),
            "vehicle_id":     str(policy.vehicle_id),
            "start_datetime": fmt_dt(policy.start_datetime),
            "end_datetime":   fmt_dt(policy.end_datetime),
            "price":          float(policy.price),
            "cover_type":     policy.cover_type,
            "status":         policy.status,
            "email_sent":     policy.email_sent,
            "issued_at":      fmt_dt(policy.issued_at),
        },
        "driver": {
            "id":               str(driver.id),
            "first_name":       driver.first_name,
            "last_name":        driver.last_name,
            "date_of_birth":    driver.date_of_birth.strftime("%Y-%m-%d") if driver.date_of_birth else "",
            "driving_licence":  driver.driving_licence,
            "email":            driver.email,
            "mobile":           driver.mobile,
            "address_line_1":   driver.address_line_1,
            "address_line_2":   driver.address_line_2 or "",
            "city":             driver.city,
            "postcode":         driver.postcode,
            "occupation":       driver.occupation,
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


# ── DELETE (cancel) policy ────────────────────────────────────────────────────

@router.delete("/{policy_id}")
def cancel_policy(
    policy_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    tenant = current_user["user"]

    policy = db.query(Policy).filter(
        Policy.id == policy_id,
        Policy.tenant_id == tenant.id,
    ).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    was_already_cancelled = policy.status == PolicyStatus.CANCELLED
    driver = policy.driver

    policy.status = PolicyStatus.CANCELLED
    db.commit()

    if not was_already_cancelled and driver and driver.email:
        background_tasks.add_task(
            send_policy_cancellation_email,
            to_email=driver.email,
            driver_name=f"{driver.first_name} {driver.last_name}",
            policy_number=policy.policy_number,
        )

    return {"message": "Policy cancelled"}


# ── PATCH update policy ──────────────────────────────────────────────────────

@router.patch("/{policy_id}", response_model=PolicyResponse)
def update_policy(
    policy_id: UUID,
    data: PolicyUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    tenant = current_user["user"]

    policy = db.query(Policy).filter(
        Policy.id == policy_id,
        Policy.tenant_id == tenant.id,
    ).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    if policy.status == PolicyStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Cannot edit a cancelled policy")

    if data.start_datetime is not None:
        policy.start_datetime = datetime.fromisoformat(data.start_datetime)
    if data.end_datetime is not None:
        policy.end_datetime = datetime.fromisoformat(data.end_datetime)
    if data.price is not None:
        policy.price = data.price
    if data.cover_type is not None:
        policy.cover_type = data.cover_type

    db.commit()
    db.refresh(policy)

    return PolicyResponse(
        id=policy.id,
        policy_number=policy.policy_number,
        driver_id=policy.driver_id,
        vehicle_id=policy.vehicle_id,
        start_datetime=fmt_dt(policy.start_datetime),
        end_datetime=fmt_dt(policy.end_datetime),
        price=float(policy.price),
        cover_type=policy.cover_type,
        status=policy.status,
        email_sent=policy.email_sent,
        issued_at=fmt_dt(policy.issued_at),
    )


# ── POST resend email ─────────────────────────────────────────────────────────

@router.post("/{policy_id}/resend-email")
def resend_email(
    policy_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    tenant = current_user["user"]

    policy = db.query(Policy).filter(
        Policy.id == policy_id,
        Policy.tenant_id == tenant.id,
    ).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    driver = db.query(Driver).filter(Driver.id == policy.driver_id).first()
    vehicle = db.query(Vehicle).filter(Vehicle.id == policy.vehicle_id).first()

    if not driver or not vehicle:
        raise HTTPException(status_code=404, detail="Driver or vehicle not found")

    background_tasks.add_task(
        _send_confirmation_email,
        policy_id=str(policy.id),
        to_email=driver.email,
        driver_name=f"{driver.first_name} {driver.last_name}",
        policy_number=policy.policy_number,
        start_datetime=fmt_dt_display(policy.start_datetime),
        end_datetime=fmt_dt_display(policy.end_datetime),
        vehicle_reg=vehicle.registration,
        vehicle_make_model=f"{vehicle.make} {vehicle.model}",
        price=str(policy.price),
        verify_token=policy.verify_token,
    )

    return {"message": "Email queued for sending"}