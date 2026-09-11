"""
Verify Router
Driver tomonidan policy hujjatlarini ko'rish uchun
Token orqali — login talab qilinmaydi
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Policy, Driver, Vehicle, StaticDocument

router = APIRouter()


class VerifyRequest(BaseModel):
    last_name: str
    date_of_birth: str    # "YYYY-MM-DD"
    start_date: str       # "YYYY-MM-DD"



@router.get("/info/{token}")
def get_verify_info(token: str, db: Session = Depends(get_db)):
    """
    Verify sahifasi yuklanganida policy_number va cover_type ni qaytaradi.
    Hech qanday shaxsiy ma'lumot bermaydi — faqat sahifa uchun kerakli info.
    """
    policy = db.query(Policy).filter(
        Policy.verify_token == token,
    ).first()

    if not policy:
        raise HTTPException(status_code=404, detail="Invalid or expired link")

    # Bekor qilingan policy ga ruxsat yo'q
    if policy.status == "cancelled":
        raise HTTPException(status_code=403, detail="This policy has been cancelled")

    return {
        "policy_number": policy.policy_number,
        "cover_type":    policy.cover_type,
    }



@router.post("/validate/{token}")
def validate_policy(
    token: str,
    data: VerifyRequest,
    db: Session = Depends(get_db),
):
    """
    Driver kiritgan ma'lumotlarni tekshiradi:
    - last_name
    - date_of_birth
    - policy start date

    To'g'ri bo'lsa — policy details va PDF linklar qaytaradi.
    """
    policy = db.query(Policy).filter(
        Policy.verify_token == token,
    ).first()

    if not policy:
        raise HTTPException(status_code=404, detail="Invalid or expired link")

    if policy.status == "cancelled":
        raise HTTPException(status_code=403, detail="This policy has been cancelled")

    driver = db.query(Driver).filter(Driver.id == policy.driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Policy data error")

    # ── Tekshirish ────────────────────────────────────────────────────────────

    # 1. Last name (case-insensitive)
    if driver.last_name.strip().lower() != data.last_name.strip().lower():
        raise HTTPException(status_code=400, detail=f"Last name mismatch: expected '{driver.last_name}' got '{data.last_name}'")

    # 2. Date of birth
    try:
        input_dob = datetime.strptime(data.date_of_birth, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    driver_dob = driver.date_of_birth
    if hasattr(driver_dob, 'date'):
        driver_dob = driver_dob.date()

    if driver_dob != input_dob:
        raise HTTPException(status_code=400, detail=f"DOB mismatch: expected '{driver_dob}' got '{input_dob}'")

    # 3. Policy start date
    try:
        input_start = datetime.strptime(data.start_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    policy_start = policy.start_datetime
    if hasattr(policy_start, 'date'):
        policy_start = policy_start.date()

    if policy_start != input_start:
        raise HTTPException(status_code=400, detail=f"Start date mismatch: expected '{policy_start}' got '{input_start}'")

    # ── Muvaffaqiyatli — verified_at ni belgilash ─────────────────────────────
    if not policy.verified_at:
        policy.verified_at = datetime.now(timezone.utc)
        db.commit()

    # ── Vehicle ma'lumotlari ──────────────────────────────────────────────────
    vehicle = db.query(Vehicle).filter(Vehicle.id == policy.vehicle_id).first()

    # ── Static hujjatlar ──────────────────────────────────────────────────────
    static_docs = db.query(StaticDocument).filter(
        StaticDocument.is_active == True
    ).all()

    static_doc_list = [
        {"name": d.name, "url": d.url}
        for d in static_docs
    ]

    # ── PDF linklar (dinamik) ──────────────────────────────────────────────────
    from app.config import settings
    base = settings.APP_URL

    return {
        "policy": {
            "policy_number":  policy.policy_number,
            "cover_type":     policy.cover_type,
            "start_datetime": _fmt_display(policy.start_datetime),
            "end_datetime":   _fmt_display(policy.end_datetime),
            "price":          str(policy.price),
        },
        "driver": {
            "first_name": driver.first_name,
            "last_name":  driver.last_name,
        },
        "vehicle": {
            "registration": vehicle.registration if vehicle else "",
            "make":         vehicle.make if vehicle else "",
            "model":        vehicle.model if vehicle else "",
        } if vehicle else {},
        "dynamic_docs": [
            {
                "name": "Certificate of Motor Insurance",
                "url":  f"{base}/api/v1/pdf/certificate/{policy.id}?token={token}",
            },
            {
                "name": "New Policy Schedule",
                "url":  f"{base}/api/v1/pdf/schedule/{policy.id}?token={token}",
            },
            {
                "name": "Statement of Fact",
                "url":  f"{base}/api/v1/pdf/statement/{policy.id}?token={token}",
            },
        ],
        "static_docs": static_doc_list,
    }


def _fmt_display(dt) -> str:
    if dt is None:
        return ""
    if hasattr(dt, 'strftime'):
        return dt.strftime("%A, %d %B %Y at %H:%M")
    return str(dt)