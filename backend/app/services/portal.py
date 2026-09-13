"""
Driver-facing policy payload — shared by the portal login and the emailed documents link.
"""

from sqlalchemy.orm import Session

from app.config import settings
from app.models.models import Policy, Driver, Vehicle, StaticDocument
from app.services.branding import cover_label
from app.services.policy_service import fmt_display


def build_portal_payload(db: Session, policy: Policy) -> dict:
    driver  = db.query(Driver).filter(Driver.id == policy.driver_id).first()
    vehicle = db.query(Vehicle).filter(Vehicle.id == policy.vehicle_id).first()
    statics = db.query(StaticDocument).filter(StaticDocument.is_active == True).order_by(StaticDocument.created_at).all()

    base, pid, tok = settings.APP_URL, policy.id, policy.verify_token
    certificate = {"name": "Certificate of Motor Insurance", "url": f"{base}/api/v1/pdf/certificate/{pid}?token={tok}", "kind": "generated"}
    schedule    = {"name": "New Policy Schedule",            "url": f"{base}/api/v1/pdf/schedule/{pid}?token={tok}",    "kind": "generated"}
    statement   = {"name": "Statement of Fact",              "url": f"{base}/api/v1/pdf/statement/{pid}?token={tok}",   "kind": "generated"}
    static_docs = [{"name": s.name, "url": s.url, "kind": "static"} for s in statics]

    # Same order a driver expects: certificate, schedule, wording/contract, statement, then everything else (e.g. IPID)
    def primary(doc):
        n = doc["name"].lower()
        return "wording" in n or "contract" in n
    documents = ([certificate, schedule]
                 + [s for s in static_docs if primary(s)]
                 + [statement]
                 + [s for s in static_docs if not primary(s)])

    status = policy.status.value if hasattr(policy.status, "value") else str(policy.status)
    return {
        "driver": {
            "first_name": driver.first_name if driver else "",
            "last_name":  driver.last_name if driver else "",
        },
        "policy": {
            "policy_number":  policy.policy_number,
            "cover_type":     policy.cover_type.value if hasattr(policy.cover_type, "value") else str(policy.cover_type),
            "cover_label":    cover_label(policy.cover_type),
            "status":         status,
            "version":        policy.version or 1,
            "start_datetime": fmt_display(policy.start_datetime),
            "end_datetime":   fmt_display(policy.end_datetime),
            "start_iso":      policy.start_datetime.isoformat() if policy.start_datetime else None,
            "end_iso":        policy.end_datetime.isoformat() if policy.end_datetime else None,
            "price":          str(policy.price),
        },
        "vehicle": {
            "registration": vehicle.registration if vehicle else "",
            "make":         vehicle.make if vehicle else "",
            "model":        vehicle.model if vehicle else "",
            "colour":       vehicle.color if vehicle else "",
        },
        "documents":    documents,
        "dynamic_docs": [certificate, schedule, statement],
        "static_docs":  static_docs,
        "support_email": settings.SUPPORT_EMAIL,
    }
