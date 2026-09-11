"""
Vehicles Router
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.models.models import Vehicle, VehicleValueRange

router = APIRouter()


class VehicleCreate(BaseModel):
    registration: str
    make: str
    model: str
    year: int
    color: Optional[str] = None
    value_range: VehicleValueRange


class VehicleUpdate(BaseModel):
    registration: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    color: Optional[str] = None
    value_range: Optional[VehicleValueRange] = None


class VehicleResponse(BaseModel):
    id: UUID
    registration: str
    make: str
    model: str
    year: int
    color: Optional[str]
    value_range: str

    class Config:
        from_attributes = True


# ── GET all vehicles ──────────────────────────────────────────────────────────

@router.get("/", response_model=List[VehicleResponse])
def get_vehicles(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    tenant = current_user["user"]
    return (
        db.query(Vehicle)
        .filter(Vehicle.tenant_id == tenant.id)
        .order_by(Vehicle.registration)
        .all()
    )


# ── POST create vehicle ───────────────────────────────────────────────────────

@router.post("/", response_model=VehicleResponse)
def create_vehicle(
    data: VehicleCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    tenant = current_user["user"]
    vehicle = Vehicle(
        tenant_id=tenant.id,
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
    return vehicle


# ── GET single vehicle ────────────────────────────────────────────────────────

@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(
    vehicle_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    tenant = current_user["user"]

    # ← MUHIM: tenant isolation
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.tenant_id == tenant.id,
    ).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


# ── PATCH update vehicle ──────────────────────────────────────────────────────

@router.patch("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: UUID,
    data: VehicleUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    tenant = current_user["user"]

    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.tenant_id == tenant.id,
    ).first()
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
    return vehicle


# ── DELETE vehicle ────────────────────────────────────────────────────────────

@router.delete("/{vehicle_id}")
def delete_vehicle(
    vehicle_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    tenant = current_user["user"]

    # ← MUHIM: tenant isolation
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.tenant_id == tenant.id,
    ).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    db.delete(vehicle)
    db.commit()
    return {"message": "Vehicle deleted"}