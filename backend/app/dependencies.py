"""
FastAPI dependencies — authentication and authorization
"""

from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.utils.security import decode_token
from app.models.models import SuperAdmin, Tenant

security = HTTPBearer()


def get_house_tenant(db: Session) -> Tenant | None:
    """The internal agent record the super admin acts as (drivers/vehicles/policies need a tenant)."""
    return db.query(Tenant).filter(Tenant.username == settings.HOUSE_TENANT_USERNAME).first()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    role    = payload.get("role")
    user_id = payload.get("sub")

    if role == "super_admin":
        user = db.query(SuperAdmin).filter(SuperAdmin.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found")

        tenant = get_house_tenant(db)
        return {
            "user":       tenant or user,   # house tenant when it exists, else the admin itself
            "role":       "super_admin",
            "superadmin": user,
        }

    if role == "admin":
        tenant = db.query(Tenant).filter(Tenant.id == user_id).first()
        if not tenant:
            raise HTTPException(status_code=401, detail="Account not found")

        if tenant.expires_at and datetime.now(timezone.utc) > tenant.expires_at:
            raise HTTPException(
                status_code=403,
                detail="Your session has expired. Please contact the administrator.",
            )
        if tenant.status != "active":
            raise HTTPException(status_code=403, detail="Your account is suspended.")

        return {"user": tenant, "role": "admin"}

    raise HTTPException(status_code=401, detail="Invalid token role")


def require_super_admin(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Super admin access required")
    return current_user


def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ("super_admin", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user
