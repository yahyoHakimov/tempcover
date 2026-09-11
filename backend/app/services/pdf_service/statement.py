"""
StatementGenerator — Statement of Fact PDF (3-page HTML template).
"""

import os
from datetime import datetime
from .models import PolicyData

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
SIG_DIR      = os.path.join(os.path.dirname(__file__), "signatures")


def _fmt(dt, fmt="%H:%M %d %B %Y") -> str:
    if dt is None: return "—"
    if isinstance(dt, str):
        try: dt = datetime.fromisoformat(dt)
        except: return dt
    return dt.strftime(fmt)


def _render(policy: PolicyData) -> str:
    template_path = os.path.join(TEMPLATE_DIR, "statement_of_fact.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()

    logo_path = f"file://{SIG_DIR}/tempcover-logo.png"

    name_parts = policy.insured_name.strip().split()
    surname    = name_parts[-1] if name_parts else ""
    forenames  = " ".join(name_parts[:-1]) if len(name_parts) > 1 else surname

    address_parts = [policy.address_line_1, policy.city, policy.postcode]
    address = ", ".join(p for p in address_parts if p)

    replacements = {
        "{{ logo_path }}":           logo_path,
        "{{ surname }}":             surname,
        "{{ forenames }}":           forenames,
        "{{ address }}":             address,
        "{{ telephone }}":           policy.telephone,
        "{{ email }}":               policy.email,
        "{{ effective_date }}":      _fmt(policy.start_datetime),
        "{{ expiry_date }}":         _fmt(policy.end_datetime),
        "{{ policy_cover }}":        policy.policy_cover,
        "{{ number_of_drivers }}":   policy.number_of_drivers,
        "{{ driver_full_name }}":    policy.insured_name,
        "{{ driver_sex }}":          policy.driver_sex,
        "{{ driver_dob }}":          policy.driver_dob,
        "{{ driver_licence_type }}": policy.driver_licence_type,
        "{{ driver_occupation }}":   policy.driver_occupation,
        "{{ vehicle_make }}":        policy.vehicle_make,
        "{{ vehicle_model }}":       policy.vehicle_model,
        "{{ vehicle_registration }}": policy.vehicle_registration,
        "{{ vehicle_value }}":       policy.value_range,
    }

    for key, value in replacements.items():
        html = html.replace(key, str(value))

    return html


class StatementGenerator:
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
        c.drawCentredString(w / 2, h - 50, "STATEMENT OF FACT")
        c.setFont("Helvetica", 10)
        c.drawString(50, h - 80,  f"Policy:  {self.policy.policy_number}")
        c.drawString(50, h - 100, f"Insured: {self.policy.insured_name}")
        c.drawString(50, h - 120, f"Vehicle: {self.policy.vehicle_registration}")
        c.save()
        buffer.seek(0)
        return buffer.read()
