"""
ScheduleGenerator — HTML template based New Business Schedule.
"""

import os
from datetime import datetime

from app.config import settings
from app.services.branding import insurer_info_text
from .models import PolicyData

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
SIG_DIR      = os.path.join(os.path.dirname(__file__), "signatures")


def _fmt(dt) -> str:
    if dt is None:
        return "—"
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except Exception:
            return dt
    return dt.strftime("%H:%M %d-%m-%Y")


def _fmt_date(dt) -> str:
    if dt is None:
        return "—"
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except Exception:
            return dt
    return dt.strftime("%d/%m/%Y")


def _render(policy: PolicyData) -> str:
    template_path = os.path.join(TEMPLATE_DIR, "schedule.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()

    try:
        compulsory = float(policy.compulsory_excess)
        voluntary  = float(policy.voluntary_excess)
        total      = compulsory + voluntary
    except Exception:
        compulsory = 500.0
        voluntary  = 0.0
        total      = 500.0

    address_parts = []
    if policy.address_line_1: address_parts.append(policy.address_line_1)
    if policy.city:           address_parts.append(policy.city)
    if policy.postcode:       address_parts.append(policy.postcode)
    address = ", ".join(address_parts) if address_parts else "—"

    replacements = {
        "{{ logo_path }}":          f"file://{SIG_DIR}/tempcover-logo.png",
        "{{ policy_number }}":      policy.policy_number,
        "{{ date_issued }}":        _fmt_date(policy.issued_at),
        "{{ agent_name }}":         policy.agent_name or settings.TRADING_NAME,
        "{{ trading_name }}":       settings.TRADING_NAME,
        "{{ insurer_info }}":       insurer_info_text(),
        "{{ version }}":            str(policy.version or 1),
        "{{ insured_name }}":       policy.insured_display,
        "{{ insured_address }}":    address,
        "{{ effective_datetime }}": _fmt(policy.start_datetime),
        "{{ expiry_datetime }}":    _fmt(policy.end_datetime),
        "{{ reason_for_issue }}":   policy.reason_for_issue or "New Business",
        "{{ premium }}":            policy.price,
        "{{ vehicle_registration }}": policy.vehicle_registration,
        "{{ cover_type }}":         (policy.policy_cover or "Fully Comprehensive").upper(),
        "{{ vehicle_value }}":      policy.value_range or "—",
        "{{ vehicle_make_model }}": policy.make_model,
        "{{ compulsory_excess }}":  f"{compulsory:.2f}",
        "{{ voluntary_excess }}":   f"{voluntary:.2f}",
        "{{ total_excess }}":       f"{total:.2f}",
    }

    for key, value in replacements.items():
        html = html.replace(key, str(value))

    return html


class ScheduleGenerator:
    def __init__(self, policy: PolicyData) -> None:
        self.policy = policy

    def generate(self) -> bytes:
        from app.services.pdf_service.utils import safe_weasyprint
        html = _render(self.policy)
        result = safe_weasyprint(html)
        if result is not None:
            return result
        return self._fallback()

    def _fallback(self) -> bytes:
        import io
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas as rl_canvas
        buffer = io.BytesIO()
        c = rl_canvas.Canvas(buffer, pagesize=A4)
        w, h = A4
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(w/2, h-50, "NEW BUSINESS SCHEDULE")
        c.setFont("Helvetica", 11)
        c.drawString(50, h-90, f"Policy: {self.policy.policy_number}")
        c.drawString(50, h-110, f"Insured: {self.policy.insured_display}")
        c.save()
        buffer.seek(0)
        return buffer.read()
