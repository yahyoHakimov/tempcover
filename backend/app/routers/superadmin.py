"""
Super Admin Router
Tenant management + All Policies + Create Policy + Settings
"""

import uuid
import random
import string
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.dependencies import require_super_admin
from app.models.models import (
    Tenant, Policy, Driver, Vehicle, StaticDocument, Payment,
    PolicyStatus, TenantStatus, TenantPlan, CoverType, VehicleValueRange
)
from app.utils.security import hash_password
from app.services.email_service import send_policy_confirmation_email, send_policy_cancellation_email
from app.config import settings

router = APIRouter()


# ── Helpers ───────────────────────────────────

def fmt_dt(dt) -> str:
    if dt is None:
        return ""
    if hasattr(dt, 'isoformat'):
        return dt.isoformat()
    return str(dt)


def generate_policy_number() -> str:
    digits = ''.join(random.choices(string.digits, k=8))
    return digits


# ── Schemas ───────────────────────────────────

class TenantCreate(BaseModel):
    name: str
    email: EmailStr
    username: str
    password: str
    phone: Optional[str] = None
    company: Optional[str] = None
    plan: TenantPlan = TenantPlan.BASIC
    monthly_fee: float = 0.0
    expires_at: Optional[datetime] = None


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    plan: Optional[TenantPlan] = None
    monthly_fee: Optional[float] = None
    expires_at: Optional[datetime] = None
    status: Optional[TenantStatus] = None
    password: Optional[str] = None


class TenantResponse(BaseModel):
    id: UUID
    name: str
    email: str
    username: str
    phone: Optional[str]
    company: Optional[str]
    plan: str
    status: str
    monthly_fee: float
    expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class DriverCreate(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: str
    driving_licence: str
    mobile: str
    email: EmailStr
    address_line_1: str
    address_line_2: Optional[str] = None
    city: str
    postcode: str
    occupation: str


class VehicleCreate(BaseModel):
    registration: str
    make: str
    model: str
    year: int
    color: Optional[str] = None
    value_range: VehicleValueRange


class PolicyCreate(BaseModel):
    tenant_id: UUID
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
    status: Optional[PolicyStatus] = None


# ── Dashboard ─────────────────────────────────

@router.get("/dashboard")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    total_tenants   = db.query(Tenant).count()
    active_tenants  = db.query(Tenant).filter(Tenant.status == "active").count()
    total_policies  = db.query(Policy).count()
    active_policies = db.query(Policy).filter(Policy.status == "active").count()

    return {
        "total_tenants":   total_tenants,
        "active_tenants":  active_tenants,
        "total_policies":  total_policies,
        "active_policies": active_policies,
    }


# ── Tenants ───────────────────────────────────

@router.get("/tenants", response_model=List[TenantResponse])
def get_tenants(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    return db.query(Tenant).order_by(Tenant.created_at.desc()).all()


@router.post("/tenants", response_model=TenantResponse)
def create_tenant(
    data: TenantCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    existing = db.query(Tenant).filter(
        (Tenant.username == data.username) | (Tenant.email == data.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    tenant = Tenant(
        name=data.name,
        email=data.email,
        username=data.username,
        password_hash=hash_password(data.password),
        phone=data.phone,
        company=data.company,
        plan=data.plan,
        monthly_fee=data.monthly_fee,
        expires_at=data.expires_at,
        status=TenantStatus.ACTIVE,
        created_by=current_user["user"].id,
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


@router.get("/tenants/{tenant_id}", response_model=TenantResponse)
def get_tenant(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@router.patch("/tenants/{tenant_id}", response_model=TenantResponse)
def update_tenant(
    tenant_id: UUID,
    data: TenantUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    if data.name:        tenant.name = data.name
    if data.email:       tenant.email = data.email
    if data.phone:       tenant.phone = data.phone
    if data.company:     tenant.company = data.company
    if data.plan:        tenant.plan = data.plan
    if data.monthly_fee is not None: tenant.monthly_fee = data.monthly_fee
    if data.expires_at:  tenant.expires_at = data.expires_at
    if data.status:      tenant.status = data.status
    if data.password:    tenant.password_hash = hash_password(data.password)

    db.commit()
    db.refresh(tenant)
    return tenant


@router.delete("/tenants/{tenant_id}")
def delete_tenant(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    db.delete(tenant)
    db.commit()
    return {"message": "Tenant deleted"}


@router.post("/tenants/{tenant_id}/suspend")
def suspend_tenant(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant.status = TenantStatus.SUSPENDED
    db.commit()
    return {"message": "Tenant suspended"}


@router.post("/tenants/{tenant_id}/activate")
def activate_tenant(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant.status = TenantStatus.ACTIVE
    db.commit()
    return {"message": "Tenant activated"}


# ── All Drivers (barcha tenantlar bo'yicha) ───

@router.get("/drivers")
def get_all_drivers(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    from app.routers.drivers import get_driver_policy_stats

    rows = (
        db.query(Driver, Tenant.name)
        .join(Tenant, Driver.tenant_id == Tenant.id)
        .order_by(Driver.first_name)
        .all()
    )
    stats = get_driver_policy_stats(db)

    result = []
    for d, agent_name in rows:
        cnt, active_cnt, last_at = stats.get(d.id, (0, 0, None))
        result.append({
            "id":              str(d.id),
            "first_name":      d.first_name,
            "last_name":       d.last_name,
            "email":           d.email,
            "mobile":          d.mobile,
            "date_of_birth": d.date_of_birth.strftime("%Y-%m-%d") if d.date_of_birth else "",
            "driving_licence": d.driving_licence,
            "address_line_1":  d.address_line_1,
            "city":            d.city,
            "postcode":        d.postcode,
            "occupation":      d.occupation,
            "agent_name":      agent_name,
            "tenant_id":       str(d.tenant_id),
            "policy_count":        cnt,
            "active_policy_count": active_cnt,
            "last_policy_at":      last_at.strftime("%Y-%m-%d") if last_at else None,
        })
    return result


# ── Tenant Drivers ────────────────────────────

@router.get("/tenants/{tenant_id}/drivers")
def get_tenant_drivers(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    drivers = db.query(Driver).filter(
        Driver.tenant_id == tenant_id
    ).order_by(Driver.first_name).all()

    from app.routers.drivers import get_driver_policy_stats
    stats = get_driver_policy_stats(db, tenant_id)

    result = []
    for d in drivers:
        cnt, active_cnt, last_at = stats.get(d.id, (0, 0, None))
        result.append({
            "id":              str(d.id),
            "first_name":      d.first_name,
            "last_name":       d.last_name,
            "email":           d.email,
            "mobile":          d.mobile,
            "date_of_birth": d.date_of_birth.strftime("%Y-%m-%d") if d.date_of_birth else "",
            "driving_licence": d.driving_licence,
            "address_line_1":  d.address_line_1,
            "city":            d.city,
            "postcode":        d.postcode,
            "occupation":      d.occupation,
            "policy_count":        cnt,
            "active_policy_count": active_cnt,
            "last_policy_at":      last_at.strftime("%Y-%m-%d") if last_at else None,
        })
    return result


@router.post("/tenants/{tenant_id}/drivers")
def create_tenant_driver(
    tenant_id: UUID,
    data: DriverCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    """Super admin agent nomidan driver yaratadi"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    driver = Driver(
        tenant_id=tenant_id,
        first_name=data.first_name,
        last_name=data.last_name,
        date_of_birth=datetime.strptime(data.date_of_birth, "%Y-%m-%d").date(),
        driving_licence=data.driving_licence,
        mobile=data.mobile,
        email=data.email,
        address_line_1=data.address_line_1,
        address_line_2=data.address_line_2,
        city=data.city,
        postcode=data.postcode,
        occupation=data.occupation,
    )
    db.add(driver)
    db.commit()
    db.refresh(driver)

    return {
        "id":              str(driver.id),
        "first_name":      driver.first_name,
        "last_name":       driver.last_name,
        "email":           driver.email,
        "mobile":          driver.mobile,
        "date_of_birth":   driver.date_of_birth.strftime("%Y-%m-%d") if driver.date_of_birth else "",
        "driving_licence": driver.driving_licence,
        "address_line_1":  driver.address_line_1,
        "city":            driver.city,
        "postcode":        driver.postcode,
        "occupation":      driver.occupation,
    }


# ── Tenant Vehicles ───────────────────────────

@router.get("/tenants/{tenant_id}/vehicles")
def get_tenant_vehicles(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    vehicles = db.query(Vehicle).filter(
        Vehicle.tenant_id == tenant_id
    ).order_by(Vehicle.registration).all()

    return [
        {
            "id":           str(v.id),
            "registration": v.registration,
            "make":         v.make,
            "model":        v.model,
            "year":         v.year,
            "value_range":  v.value_range.value if hasattr(v.value_range, 'value') else str(v.value_range),
        }
        for v in vehicles
    ]


@router.post("/tenants/{tenant_id}/vehicles")
def create_tenant_vehicle(
    tenant_id: UUID,
    data: VehicleCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    """Super admin agent nomidan vehicle yaratadi"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    vehicle = Vehicle(
        tenant_id=tenant_id,
        registration=data.registration.upper().strip(),
        make=data.make.upper(),
        model=data.model.upper(),
        year=data.year,
        color=data.color,
        value_range=data.value_range,
    )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)

    return {
        "id":           str(vehicle.id),
        "registration": vehicle.registration,
        "make":         vehicle.make,
        "model":        vehicle.model,
        "year":         vehicle.year,
        "value_range":  vehicle.value_range.value if hasattr(vehicle.value_range, 'value') else str(vehicle.value_range),
    }


# ── Driver / Vehicle update (superadmin) ─────

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


class VehicleUpdate(BaseModel):
    registration: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    color: Optional[str] = None
    value_range: Optional[VehicleValueRange] = None


@router.patch("/drivers/{driver_id}")
def update_driver(
    driver_id: UUID,
    data: DriverUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    if data.first_name is not None:      driver.first_name      = data.first_name
    if data.last_name is not None:       driver.last_name       = data.last_name
    if data.date_of_birth is not None:   driver.date_of_birth   = datetime.strptime(data.date_of_birth, "%Y-%m-%d").date()
    if data.driving_licence is not None: driver.driving_licence = data.driving_licence
    if data.mobile is not None:          driver.mobile          = data.mobile
    if data.email is not None:           driver.email           = data.email
    if data.address_line_1 is not None:  driver.address_line_1  = data.address_line_1
    if data.address_line_2 is not None:  driver.address_line_2  = data.address_line_2
    if data.city is not None:            driver.city            = data.city
    if data.postcode is not None:        driver.postcode        = data.postcode
    if data.occupation is not None:      driver.occupation      = data.occupation

    db.commit()
    db.refresh(driver)
    return {
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
    }


@router.delete("/drivers/{driver_id}")
def delete_driver(
    driver_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
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


@router.patch("/vehicles/{vehicle_id}")
def update_vehicle(
    vehicle_id: UUID,
    data: VehicleUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    if data.registration is not None: vehicle.registration = data.registration.upper().strip()
    if data.make is not None:         vehicle.make         = data.make.upper()
    if data.model is not None:        vehicle.model        = data.model.upper()
    if data.year is not None:         vehicle.year         = data.year
    if data.color is not None:        vehicle.color        = data.color
    if data.value_range is not None:  vehicle.value_range  = data.value_range

    db.commit()
    db.refresh(vehicle)
    return {
        "id":           str(vehicle.id),
        "registration": vehicle.registration,
        "make":         vehicle.make,
        "model":        vehicle.model,
        "year":         vehicle.year,
        "color":        vehicle.color or "",
        "value_range":  vehicle.value_range.value if hasattr(vehicle.value_range, "value") else str(vehicle.value_range),
    }


# ── Policies ──────────────────────────────────

@router.get("/policies")
def get_all_policies(
    tenant_id: Optional[UUID] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    query = db.query(Policy, Tenant).join(Tenant, Policy.tenant_id == Tenant.id)

    if tenant_id:
        query = query.filter(Policy.tenant_id == tenant_id)
    if status:
        query = query.filter(Policy.status == status)

    results = query.order_by(Policy.issued_at.desc()).all()

    # Auto-expire policies
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    for policy, tenant in results:
        if policy.status.value == "active" and policy.end_datetime and policy.end_datetime < now:
            policy.status = PolicyStatus.EXPIRED
    db.commit()

    policies = []
    for policy, tenant in results:
        driver  = db.query(Driver).filter(Driver.id == policy.driver_id).first()
        vehicle = db.query(Vehicle).filter(Vehicle.id == policy.vehicle_id).first()

        policies.append({
            "id":             str(policy.id),
            "policy_number":  policy.policy_number,
            "status":         policy.status,
            "cover_type":     policy.cover_type,
            "price":          float(policy.price),
            "start_datetime": fmt_dt(policy.start_datetime),
            "end_datetime":   fmt_dt(policy.end_datetime),
            "email_sent":     policy.email_sent,
            "issued_at":      fmt_dt(policy.issued_at),
            "agent": {
                "id":       str(tenant.id),
                "name":     tenant.name,
                "username": tenant.username,
            },
            "driver": {
                "first_name": driver.first_name if driver else "",
                "last_name":  driver.last_name  if driver else "",
                "email":      driver.email       if driver else "",
            } if driver else None,
            "vehicle": {
                "registration": vehicle.registration if vehicle else "",
                "make":         vehicle.make         if vehicle else "",
                "model":        vehicle.model        if vehicle else "",
            } if vehicle else None,
        })

    return policies


@router.post("/policies")
def create_policy(
    data: PolicyCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    tenant = db.query(Tenant).filter(Tenant.id == data.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Agent not found")

    driver = db.query(Driver).filter(
        Driver.id == data.driver_id,
        Driver.tenant_id == data.tenant_id,
    ).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    vehicle = db.query(Vehicle).filter(
        Vehicle.id == data.vehicle_id,
        Vehicle.tenant_id == data.tenant_id,
    ).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    policy_number = generate_policy_number()
    verify_token = str(uuid.uuid4()).replace('-', '')[:32]

    policy = None
    for _ in range(10):
        policy = Policy(
            tenant_id=data.tenant_id,
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

    background_tasks.add_task(
        _send_confirmation_email,
        policy_id=str(policy.id),
        to_email=driver.email,
        driver_name=f"{driver.first_name} {driver.last_name}",
        policy_number=policy.policy_number,
        start_datetime=policy.start_datetime.strftime("%d %B %Y at %H:%M") if hasattr(policy.start_datetime, 'strftime') else str(policy.start_datetime),
        end_datetime=policy.end_datetime.strftime("%d %B %Y at %H:%M") if hasattr(policy.end_datetime, 'strftime') else str(policy.end_datetime),
        vehicle_reg=vehicle.registration,
        vehicle_make_model=f"{vehicle.make} {vehicle.model}",
        price=str(policy.price),
        verify_token=policy.verify_token,
    )

    return {
        "id":            str(policy.id),
        "policy_number": policy.policy_number,
        "status":        policy.status,
        "issued_at":     fmt_dt(policy.issued_at),
    }


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
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.models.models import Policy as PolicyModel

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
                from datetime import datetime, timezone
                p.email_sent = True
                p.email_sent_at = datetime.now(timezone.utc)
                db.commit()
    finally:
        db.close()


@router.get("/policies/{policy_id}")
def get_policy_detail(
    policy_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    tenant  = db.query(Tenant).filter(Tenant.id == policy.tenant_id).first()
    driver  = db.query(Driver).filter(Driver.id == policy.driver_id).first()
    vehicle = db.query(Vehicle).filter(Vehicle.id == policy.vehicle_id).first()

    return {
        "policy": {
            "id":                str(policy.id),
            "policy_number":     policy.policy_number,
            "driver_id":         str(policy.driver_id),
            "vehicle_id":        str(policy.vehicle_id),
            "status":            policy.status,
            "cover_type":        policy.cover_type,
            "price":             float(policy.price),
            "start_datetime":    fmt_dt(policy.start_datetime),
            "end_datetime":      fmt_dt(policy.end_datetime),
            "compulsory_excess": float(policy.compulsory_excess),
            "voluntary_excess":  float(policy.voluntary_excess),
            "email_sent":        policy.email_sent,
            "issued_at":         fmt_dt(policy.issued_at),
        },
        "agent": {
            "id":       str(tenant.id),
            "name":     tenant.name,
            "username": tenant.username,
            "email":    tenant.email,
        } if tenant else None,
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


@router.patch("/policies/{policy_id}")
def update_policy(
    policy_id: UUID,
    data: PolicyUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    if data.start_datetime is not None:
        policy.start_datetime = datetime.fromisoformat(data.start_datetime)
    if data.end_datetime is not None:
        policy.end_datetime = datetime.fromisoformat(data.end_datetime)
    if data.price is not None:
        policy.price = data.price
    if data.cover_type is not None:
        policy.cover_type = data.cover_type
    if data.status is not None:
        policy.status = data.status

    db.commit()
    db.refresh(policy)

    return {
        "id":             str(policy.id),
        "policy_number":  policy.policy_number,
        "status":         policy.status,
        "cover_type":     policy.cover_type,
        "price":          float(policy.price),
        "start_datetime": fmt_dt(policy.start_datetime),
        "end_datetime":   fmt_dt(policy.end_datetime),
        "email_sent":     policy.email_sent,
        "issued_at":      fmt_dt(policy.issued_at),
    }


@router.delete("/policies/{policy_id}")
def cancel_policy(
    policy_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
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


@router.delete("/policies/{policy_id}/permanent")
def delete_policy(
    policy_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    db.query(Payment).filter(Payment.policy_id == policy.id).delete()
    db.delete(policy)
    db.commit()
    return {"message": "Policy deleted"}


# ── Settings ──────────────────────────────────

@router.get("/settings/documents")
def get_static_documents(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    docs = db.query(StaticDocument).order_by(StaticDocument.created_at.desc()).all()
    return [
        {
            "id":         str(d.id),
            "name":       d.name,
            "url":        d.url,
            "version":    d.version,
            "is_active":  d.is_active,
            "created_at": fmt_dt(d.created_at),
        }
        for d in docs
    ]


class DocumentCreate(BaseModel):
    name: str
    url: str
    version: Optional[str] = None


@router.post("/settings/documents")
def add_static_document(
    data: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    doc = StaticDocument(name=data.name, url=data.url, version=data.version, is_active=True)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return {
        "id":         str(doc.id),
        "name":       doc.name,
        "url":        doc.url,
        "version":    doc.version,
        "is_active":  doc.is_active,
        "created_at": fmt_dt(doc.created_at),
    }


@router.delete("/settings/documents/{doc_id}")
def delete_static_document(
    doc_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    doc = db.query(StaticDocument).filter(StaticDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()
    return {"message": "Document deleted"}


@router.patch("/settings/documents/{doc_id}/toggle")
def toggle_static_document(
    doc_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    doc = db.query(StaticDocument).filter(StaticDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    doc.is_active = not doc.is_active
    db.commit()
    return {"id": str(doc.id), "is_active": doc.is_active}

# ── Static Document File Upload ───────────────────────────────────────────────

import os
import shutil
from fastapi import UploadFile, File, Form

UPLOAD_DIR = os.path.join(settings.STATIC_DIR, "docs")

@router.post("/settings/documents/upload")
async def upload_static_document(
    name: str = Form(...),
    version: str = Form(""),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Sanitize filename: strip directory components and allow only safe characters
    from pathlib import Path
    safe_name = Path(file.filename).name
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in "._-")
    if not safe_name:
        raise HTTPException(status_code=400, detail="Invalid filename")
    filepath = os.path.join(UPLOAD_DIR, safe_name)

    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    url = f"{settings.APP_URL}/static/docs/{safe_name}"

    doc = StaticDocument(name=name, url=url, version=version, is_active=True)
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {
        "id":         str(doc.id),
        "name":       doc.name,
        "url":        doc.url,
        "version":    doc.version,
        "is_active":  doc.is_active,
        "created_at": fmt_dt(doc.created_at),
    }
