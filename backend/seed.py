"""
First-run seed — creates the super admin and the internal "house" agent.

    SEED_SUPERADMIN_PASSWORD=... python seed.py

Safe to run repeatedly: existing records are left untouched.
"""

import secrets

from app.config import settings
from app.database import SessionLocal, engine, Base
from app.models.models import SuperAdmin, Tenant, TenantStatus, TenantPlan
from app.utils.security import hash_password


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not settings.SEED_SUPERADMIN_PASSWORD:
            print("SEED_SUPERADMIN_PASSWORD is empty — no super admin created.")
        elif db.query(SuperAdmin).filter(SuperAdmin.username == settings.SEED_SUPERADMIN_USERNAME).first():
            print(f"Super admin '{settings.SEED_SUPERADMIN_USERNAME}' already exists.")
        else:
            db.add(SuperAdmin(
                username=settings.SEED_SUPERADMIN_USERNAME,
                email=settings.SEED_SUPERADMIN_EMAIL,
                full_name=settings.SEED_SUPERADMIN_NAME,
                password_hash=hash_password(settings.SEED_SUPERADMIN_PASSWORD),
                is_active=True,
            ))
            print(f"Created super admin '{settings.SEED_SUPERADMIN_USERNAME}'.")

        if db.query(Tenant).filter(Tenant.username == settings.HOUSE_TENANT_USERNAME).first():
            print(f"House agent '{settings.HOUSE_TENANT_USERNAME}' already exists.")
        else:
            db.add(Tenant(
                name="TempCover HQ",
                company="TempCover",
                email=f"{settings.HOUSE_TENANT_USERNAME}@tempcover-verify.com",
                username=settings.HOUSE_TENANT_USERNAME,
                # Not meant for logging in — random, unrecoverable password
                password_hash=hash_password(secrets.token_urlsafe(32)),
                plan=TenantPlan.ENTERPRISE,
                status=TenantStatus.ACTIVE,
            ))
            print(f"Created house agent '{settings.HOUSE_TENANT_USERNAME}'.")

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()
