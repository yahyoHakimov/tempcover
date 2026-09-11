# backend/app/routers/pdf_router.py
import io
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import require_admin
from app.models.models import Policy
from app.services.pdf_service.service import PDFService

router = APIRouter(prefix="/api/v1/pdf", tags=["PDF"])


def _get_policy_by_id(policy_id: uuid.UUID, db: Session) -> Policy:
    policy = (
        db.query(Policy)
        .options(joinedload(Policy.driver), joinedload(Policy.vehicle))
        .filter(Policy.id == policy_id)
        .first()
    )
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


def _get_policy_by_token(policy_id: uuid.UUID, token: str, db: Session) -> Policy:
    policy = (
        db.query(Policy)
        .options(joinedload(Policy.driver), joinedload(Policy.vehicle))
        .filter(Policy.id == policy_id, Policy.verify_token == token)
        .first()
    )
    if not policy:
        raise HTTPException(status_code=404, detail="Invalid link or policy not found")
    if policy.status == "cancelled":
        raise HTTPException(status_code=403, detail="Policy has been cancelled")
    return policy


# ── Admin endpoints — JWT bilan ───────────────────────────────────────────────

@router.get("/admin/certificate/{policy_id}")
def admin_get_certificate(
    policy_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    tenant = current_user["user"]
    policy = _get_policy_by_id(policy_id, db)
    if str(policy.tenant_id) != str(tenant.id):
        raise HTTPException(status_code=403, detail="Access denied")
    pdf = PDFService.certificate(policy)
    return StreamingResponse(
        io.BytesIO(pdf), media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="cert_{policy.policy_number}.pdf"'},
    )


@router.get("/admin/schedule/{policy_id}")
def admin_get_schedule(
    policy_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    tenant = current_user["user"]
    policy = _get_policy_by_id(policy_id, db)
    if str(policy.tenant_id) != str(tenant.id):
        raise HTTPException(status_code=403, detail="Access denied")
    pdf = PDFService.schedule(policy)
    return StreamingResponse(
        io.BytesIO(pdf), media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="schedule_{policy.policy_number}.pdf"'},
    )


@router.get("/admin/combined/{policy_id}")
def admin_get_combined(
    policy_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    tenant = current_user["user"]
    policy = _get_policy_by_id(policy_id, db)
    if str(policy.tenant_id) != str(tenant.id):
        raise HTTPException(status_code=403, detail="Access denied")
    pdf = PDFService.combined(policy)
    return StreamingResponse(
        io.BytesIO(pdf), media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="policy_{policy.policy_number}.pdf"'},
    )


# ── Driver endpoints — verify_token bilan ────────────────────────────────────

@router.get("/certificate/{policy_id}")
def get_certificate(
    policy_id: uuid.UUID,
    token: str = Query(...),
    db: Session = Depends(get_db),
):
    policy = _get_policy_by_token(policy_id, token, db)
    pdf = PDFService.certificate(policy)
    return StreamingResponse(
        io.BytesIO(pdf), media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="cert_{policy.policy_number}.pdf"'},
    )


@router.get("/schedule/{policy_id}")
def get_schedule(
    policy_id: uuid.UUID,
    token: str = Query(...),
    db: Session = Depends(get_db),
):
    policy = _get_policy_by_token(policy_id, token, db)
    pdf = PDFService.schedule(policy)
    return StreamingResponse(
        io.BytesIO(pdf), media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="schedule_{policy.policy_number}.pdf"'},
    )


@router.get("/combined/{policy_id}")
def get_combined(
    policy_id: uuid.UUID,
    token: str = Query(...),
    db: Session = Depends(get_db),
):
    policy = _get_policy_by_token(policy_id, token, db)
    pdf = PDFService.combined(policy)
    return StreamingResponse(
        io.BytesIO(pdf), media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="policy_{policy.policy_number}.pdf"'},
    )


@router.get("/statement/{policy_id}")
def get_statement(
    policy_id: uuid.UUID,
    token: str = Query(...),
    db: Session = Depends(get_db),
):
    policy = _get_policy_by_token(policy_id, token, db)
    pdf = PDFService.statement(policy)
    return StreamingResponse(
        io.BytesIO(pdf), media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="statement_{policy.policy_number}.pdf"'},
    )