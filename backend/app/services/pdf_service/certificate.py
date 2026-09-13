"""
CertificateGenerator — HTML template based Certificate of Motor Insurance.
"""

import os
from datetime import datetime

from app.config import settings
from app.services.branding import legal_footer_text
from .models import PolicyData

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
SIG_DIR      = os.path.join(os.path.dirname(__file__), "signatures")


def _fmt(dt, fmt="%H:%M hrs %d/%m/%Y") -> str:
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

    logo_path = f"file://{SIG_DIR}/tempcover-logo.png"
    sign_path = f"file://{SIG_DIR}/sign.png"

    replacements = {
        "{{ policy_number }}":        policy.policy_number,
        "{{ policy_suffix }}":        "",
        "{{ date_of_issue }}":        _fmt_date(policy.issued_at),
        "{{ vehicle_registration }}": policy.vehicle_registration,
        "{{ vehicle_description }}":  f"{policy.vehicle_make} {policy.vehicle_model}",
        "{{ insured_name }}":         policy.insured_display,
        "{{ effective_datetime }}":   _fmt(policy.start_datetime),
        "{{ expiry_datetime }}":      _fmt(policy.end_datetime),
        "{{ logo_path }}":            logo_path,
        "{{ sign_path }}":            sign_path,
        "{{ company_legal_name }}":   settings.COMPANY_LEGAL_NAME,
        "{{ legal_footer }}":         legal_footer_text(),
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
