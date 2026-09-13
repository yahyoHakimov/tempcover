"""
First-run seed — creates the super admin, the internal "house" agent and the
three static documents every driver sees (Policy Wording, IPID, contract).

    SEED_SUPERADMIN_PASSWORD=... python seed.py

Safe to run repeatedly: existing records are left untouched.
"""

import os
import secrets
import shutil

from app.config import settings
from app.database import SessionLocal, engine, Base
from app.models.models import SuperAdmin, Tenant, TenantStatus, TenantPlan, StaticDocument
from app.utils.security import hash_password

# Asl Tempcover / First Underwriting hujjatlari — repo bilan birga keladi
# (app/static_docs), ishga tushganda STATIC_DIR/docs ga ko'chiriladi va
# superadmin yuklagan hujjatlar bilan bir xil ko'rinishda ro'yxatga olinadi.
BUNDLED_DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app", "static_docs")
STATIC_DOCUMENTS = [
    ("Policy Wording",                                "policy-wording.pdf"),
    ("Insurance Product Information Document (IPID)", "insurance-product-information.pdf"),
    ("Your Contract with Tempcover",                  "your-contract-with-tempcover.pdf"),
]


def seed_static_documents(db) -> None:
    """Copies the bundled PDFs into the served folder and registers them once."""
    docs_dir = os.path.join(settings.STATIC_DIR, "docs")
    os.makedirs(docs_dir, exist_ok=True)

    for name, filename in STATIC_DOCUMENTS:
        src = os.path.join(BUNDLED_DOCS_DIR, filename)
        dst = os.path.join(docs_dir, filename)
        if not os.path.exists(src):
            print(f"Bundled document missing, skipped: {src}")
            continue
        if not os.path.exists(dst):
            shutil.copyfile(src, dst)

        if db.query(StaticDocument).filter(StaticDocument.name == name).first():
            print(f"Static document '{name}' already exists.")
            continue
        # Superadmin yuklaganidagi bilan bir xil manzil formati.
        db.add(StaticDocument(name=name, url=f"{settings.APP_URL}/static/docs/{filename}", is_active=True))
        print(f"Registered static document '{name}'.")


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
                email=f"{settings.HOUSE_TENANT_USERNAME}@tempcovermyaccount.com",
                username=settings.HOUSE_TENANT_USERNAME,
                # Not meant for logging in — random, unrecoverable password
                password_hash=hash_password(secrets.token_urlsafe(32)),
                plan=TenantPlan.ENTERPRISE,
                status=TenantStatus.ACTIVE,
            ))
            print(f"Created house agent '{settings.HOUSE_TENANT_USERNAME}'.")

        seed_static_documents(db)
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()
