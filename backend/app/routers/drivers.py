"""
Drivers Router
Agent o'z driverlarini boshqaradi
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.models.models import Driver, Policy, Payment, PolicyStatus

router = APIRouter()


class DriverCreate(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: str           # "YYYY-MM-DD"
    driving_licence: str
    mobile: str
    email: EmailStr
    address_line_1: str
    address_line_2: Optional[str] = None
    city: str
    postcode: str
    occupation: str
    sex: Optional[str] = None          # "Male" / "Female"


class DriverUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    driving_licence: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[EmailStr] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    city: Optional[str] = None
    postcode: Optional[str] = None
    occupation: Optional[str] = None
    sex: Optional[str] = None


class DriverResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    date_of_birth: str
    driving_licence: str
    mobile: str
    email: str
    address_line_1: str
    address_line_2: Optional[str]
    city: str
    postcode: str
    occupation: str
    sex: Optional[str] = None

    # Polisa statistikasi (faqat list endpointda to'ldiriladi)
    policy_count: int = 0
    active_policy_count: int = 0
    last_policy_at: Optional[str] = None

    class Config:
        from_attributes = True


def _fmt_dob(d) -> str:
    """date yoki datetime → 'YYYY-MM-DD' string"""
    if d is None:
        return ""
    if hasattr(d, 'strftime'):
        return d.strftime("%Y-%m-%d")
    return str(d)


def get_driver_policy_stats(db: Session, tenant_id=None) -> dict:
    """Bitta so'rovda: driver_id -> (policy_count, active_policy_count, last_policy_at).
    tenant_id=None bo'lsa barcha tenantlar bo'yicha (superadmin uchun)."""
    now = datetime.now(timezone.utc)
    q = db.query(
        Policy.driver_id,
        func.count(Policy.id),
        func.sum(
            case(
                (
                    Policy.status.in_([PolicyStatus.ACTIVE, PolicyStatus.PENDING])
                    & (Policy.end_datetime >= now),
                    1,
                ),
                else_=0,
            )
        ),
        func.max(Policy.issued_at),
    )
    if tenant_id is not None:
        q = q.filter(Policy.tenant_id == tenant_id)
    rows = q.group_by(Policy.driver_id).all()
    return {r[0]: (r[1], int(r[2] or 0), r[3]) for r in rows}


# ── GET all drivers ───────────────────────────────────────────────────────────

@router.get("/", response_model=List[DriverResponse])
def get_drivers(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    tenant = current_user["user"]
    drivers = (
        db.query(Driver)
        .filter(Driver.tenant_id == tenant.id)
        .order_by(Driver.first_name)
        .all()
    )
    stats = get_driver_policy_stats(db, tenant.id)
    for d in drivers:
        d.date_of_birth = _fmt_dob(d.date_of_birth)
        cnt, active_cnt, last_at = stats.get(d.id, (0, 0, None))
        d.policy_count = cnt
        d.active_policy_count = active_cnt
        d.last_policy_at = last_at.strftime("%Y-%m-%d") if last_at else None
    return drivers


# ── POST create driver ────────────────────────────────────────────────────────

@router.post("/", response_model=DriverResponse)
def create_driver(
    data: DriverCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    tenant = current_user["user"]
    driver = Driver(
        tenant_id=tenant.id,
        first_name=data.first_name,
        last_name=data.last_name,
        date_of_birth=datetime.strptime(data.date_of_birth, "%Y-%m-%d").date(),  # ← .date()
        driving_licence=data.driving_licence,
        mobile=data.mobile,
        email=data.email,
        address_line_1=data.address_line_1,
        address_line_2=data.address_line_2,
        city=data.city,
        postcode=data.postcode,
        occupation=data.occupation,
        sex=data.sex,
    )
    db.add(driver)
    db.commit()
    db.refresh(driver)
    driver.date_of_birth = _fmt_dob(driver.date_of_birth)
    return driver


# ── GET single driver ─────────────────────────────────────────────────────────

@router.get("/{driver_id}", response_model=DriverResponse)
def get_driver(
    driver_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    tenant = current_user["user"]

    # ← MUHIM: tenant isolation
    driver = db.query(Driver).filter(
        Driver.id == driver_id,
        Driver.tenant_id == tenant.id,
    ).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    driver.date_of_birth = _fmt_dob(driver.date_of_birth)
    return driver


# ── PATCH update driver ───────────────────────────────────────────────────────

@router.patch("/{driver_id}", response_model=DriverResponse)
def update_driver(
    driver_id: UUID,
    data: DriverUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    tenant = current_user["user"]

    driver = db.query(Driver).filter(
        Driver.id == driver_id,
        Driver.tenant_id == tenant.id,
    ).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    if data.first_name is not None:    driver.first_name    = data.first_name
    if data.last_name is not None:     driver.last_name     = data.last_name
    if data.date_of_birth is not None: driver.date_of_birth = datetime.strptime(data.date_of_birth, "%Y-%m-%d").date()
    if data.driving_licence is not None: driver.driving_licence = data.driving_licence
    if data.mobile is not None:        driver.mobile        = data.mobile
    if data.email is not None:         driver.email         = data.email
    if data.address_line_1 is not None: driver.address_line_1 = data.address_line_1
    if data.address_line_2 is not None: driver.address_line_2 = data.address_line_2
    if data.city is not None:          driver.city          = data.city
    if data.postcode is not None:      driver.postcode      = data.postcode
    if data.occupation is not None:    driver.occupation    = data.occupation
    if data.sex is not None:           driver.sex           = data.sex

    db.commit()
    db.refresh(driver)
    driver.date_of_birth = _fmt_dob(driver.date_of_birth)
    return driver


# ── DELETE driver ─────────────────────────────────────────────────────────────

@router.delete("/{driver_id}")
def delete_driver(
    driver_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    tenant = current_user["user"]

    # ← MUHIM: tenant isolation
    driver = db.query(Driver).filter(
        Driver.id == driver_id,
        Driver.tenant_id == tenant.id,
    ).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    now = datetime.now(timezone.utc)
    policies = db.query(Policy).filter(Policy.driver_id == driver.id).all()

    # Auto-expire policies
    for p in policies:
        if p.status == PolicyStatus.ACTIVE and p.end_datetime and p.end_datetime < now:
            p.status = PolicyStatus.EXPIRED

    # Aktiv sug'urtasi bor driverni o'chirib bo'lmaydi
    live = [
        p for p in policies
        if p.status in (PolicyStatus.ACTIVE, PolicyStatus.PENDING)
        and not (p.end_datetime and p.end_datetime < now)
    ]
    if live:
        db.commit()
        raise HTTPException(
            status_code=409,
            detail=f"This driver has {len(live)} active or pending "
                   f"{'policy' if len(live) == 1 else 'policies'}. "
                   f"Cancel them before deleting the driver.",
        )

    # Eski (cancelled/expired) polisalarni payment'lari bilan o'chiramiz (FK constraint)
    policy_ids = [p.id for p in policies]
    if policy_ids:
        db.query(Payment).filter(Payment.policy_id.in_(policy_ids)).delete(synchronize_session=False)
        db.query(Policy).filter(Policy.id.in_(policy_ids)).delete(synchronize_session=False)

    db.delete(driver)
    db.commit()
    return {"message": "Driver deleted"}


# ── Driver Portal Login ───────────────────────────────────────────────────────

class DriverLoginRequest(BaseModel):
    policy_number: str
    last_name: str
    date_of_birth: str  # YYYY-MM-DD


@router.post("/portal/login")
def driver_portal_login(
    data: DriverLoginRequest,
    db: Session = Depends(get_db),
):
    """Driver self-service: policy number + surname + date of birth → policy details and document links."""
    from app.services.policy_service import normalise_policy_number
    from app.services.portal import build_portal_payload

    policy = db.query(Policy).filter(
        Policy.policy_number == normalise_policy_number(data.policy_number)
    ).first()
    if not policy:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if "cancelled" in str(policy.status).lower():
        raise HTTPException(status_code=403, detail="This policy has been cancelled")

    driver = db.query(Driver).filter(Driver.id == policy.driver_id).first()
    if not driver or driver.last_name.strip().lower() != data.last_name.strip().lower():
        raise HTTPException(status_code=400, detail="Invalid credentials")

    try:
        input_dob = datetime.strptime(data.date_of_birth, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    driver_dob = driver.date_of_birth.date() if hasattr(driver.date_of_birth, "date") else driver.date_of_birth
    if driver_dob != input_dob:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return build_portal_payload(db, policy)


# ── GET current active static documents (public, for driver portal refresh) ──

@router.get("/portal/documents")
def get_portal_documents(db: Session = Depends(get_db)):
    from app.models.models import StaticDocument
    docs = db.query(StaticDocument).filter(StaticDocument.is_active == True).all()
    return [{"name": d.name, "url": d.url} for d in docs]