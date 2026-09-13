"""
CertificateGenerator — HTML template based Certificate of Motor Insurance.
"""

import os
from datetime import datetime

from app.config import settings
from .models import PolicyData

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
SIG_DIR      = os.path.join(os.path.dirname(__file__), "signatures")


def _fmt(dt, fmt="%H:%M %d-%m-%Y") -> str:   # asl: "21:18 11-09-2026"
    if dt is None: return "—"
    if isinstance(dt, str):
        try: dt = datetime.fromisoformat(dt)
        except: return dt
    return dt.strftime(fmt)

def _fmt_date(dt) -> str:
    if dt is None: return "—"
    if isinstance(dt, str):
        try: dt = datetime.fromisoformat(dt)
        except: return dt
    return dt.strftime("%d %b %Y")


def _render(policy: PolicyData) -> str:
    template_path = os.path.join(TEMPLATE_DIR, "certificate.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Rasmlar asl First Underwriting sertifikatidan kesib olingan.
    replacements = {
        "{{ policy_number }}":        policy.policy_number,
        "{{ vehicle_registration }}": policy.vehicle_registration,
        "{{ insured_name }}":         policy.insured_name,        # aslida unvonsiz: "Harry Potter"
        "{{ effective_datetime }}":   _fmt(policy.start_datetime),
        "{{ expiry_datetime }}":      _fmt(policy.end_datetime),
        "{{ claims_hotline }}":       settings.CLAIMS_HOTLINE,
        "{{ logo_fu }}":              f"file://{SIG_DIR}/first-underwriting.png",
        "{{ logo_tc_blue }}":         f"file://{SIG_DIR}/tempcover-logo-blue.png",
        "{{ sig_left }}":             f"file://{SIG_DIR}/sig_adam_cobourn.png",
        "{{ sig_right }}":            f"file://{SIG_DIR}/sig_tom_donachie.png",
    }

    for key, value in replacements.items():
        html = html.replace(key, str(value))

    return html


class CertificateGenerator:
    def __init__(self, policy: PolicyData) -> None:
        self.policy = policy

    def generate(self) -> bytes:
        from app.services.pdf_service.utils import safe_weasyprint
        html = _render(self.policy)
        result = safe_weasyprint(html)
        if result is not None:
            return result
        return self._fallback()

    def _fallback(self, error="") -> bytes:
        import io
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas as rl_canvas
        buffer = io.BytesIO()
        c = rl_canvas.Canvas(buffer, pagesize=A4)
        w, h = A4
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(w/2, h-50, "CERTIFICATE OF MOTOR INSURANCE")
        c.setFont("Helvetica", 10)
        c.drawString(50, h-80, f"Policy: {self.policy.policy_number}")
        c.drawString(50, h-100, f"Insured: {self.policy.insured_display}")
        c.drawString(50, h-120, f"Vehicle: {self.policy.vehicle_registration}")
        if error:
            c.setFont("Helvetica", 8)
            c.drawString(50, h-150, f"WeasyPrint error: {error[:100]}")
        c.save()
        buffer.seek(0)
        return buffer.read()
