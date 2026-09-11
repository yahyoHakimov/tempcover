"""
Auth Router
Login for Super Admin and Tenant (Agent)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.dependencies import get_current_user
from app.models.models import SuperAdmin, Tenant
from app.utils.security import verify_password, create_access_token, create_refresh_token

router = APIRouter()


# ── Schemas ──────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str
    user_id: str
    username: str
    name: str


# ── Endpoints ────────────────────────────────

@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Universal login — username va password bilan kirish.
    Avval SuperAdmin dan qidiradi, keyin Tenant dan.
    """

    # 1. Super Admin tekshirish
    super_admin = db.query(SuperAdmin).filter(
        SuperAdmin.username == data.username
    ).first()

    if super_admin and verify_password(data.password, super_admin.password_hash):
        if not super_admin.is_active:
            raise HTTPException(status_code=403, detail="Account is disabled")

        access_token = create_access_token({
            "sub": str(super_admin.id),
            "role": "super_admin",
            "username": super_admin.username,
        })
        refresh_token = create_refresh_token({"sub": str(super_admin.id)})

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            role="super_admin",
            user_id=str(super_admin.id),
            username=super_admin.username,
            name=super_admin.full_name,
        )

    # 2. Tenant (Agent) tekshirish
    tenant = db.query(Tenant).filter(
        Tenant.username == data.username
    ).first()

    if tenant and verify_password(data.password, tenant.password_hash):
        from datetime import datetime, timezone
        if tenant.expires_at and datetime.now(timezone.utc) > tenant.expires_at:
            raise HTTPException(
                status_code=403,
                detail="Your session has expired. Contact administrator.",
            )

        if tenant.status != "active":
            raise HTTPException(
                status_code=403,
                detail=f"Account is {tenant.status}.",
            )

        access_token = create_access_token({
            "sub": str(tenant.id),
            "role": "admin",
            "username": tenant.username,
        })
        refresh_token = create_refresh_token({"sub": str(tenant.id)})

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            role="admin",
            user_id=str(tenant.id),
            username=tenant.username,
            name=tenant.name,
        )

    # 3. Hech kim topilmadi
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
    )


@router.post("/logout")
def logout():
    """Client side token ni o'chiradi"""
    return {"message": "Logged out successfully"}


@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    """Current user ma'lumotlari — frontend admin page uchun"""
    user = current_user["user"]
    role = current_user["role"]

    # Super Admin va Tenant uchun alohida field lar bor
    # (full_name vs name, expires_at faqat Tenant da bor)
    name = getattr(user, "full_name", None) or getattr(user, "name", "")
    expires_at = getattr(user, "expires_at", None)

    return {
        "role": role,
        "user": {
            "id":         str(user.id),
            "username":   user.username,
            "name":       name,
            "expires_at": expires_at.isoformat() if expires_at else None,
        },
    }