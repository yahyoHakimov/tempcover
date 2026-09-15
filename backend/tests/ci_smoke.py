"""
CI smoke test — pytest'siz, oddiy skript:  python tests/ci_smoke.py  (backend/ ichidan)

Nimani tekshiradi:
  * uchala PDF haqiqatan WeasyPrint bilan yaratiladi (ReportLab fallback emas)
    va asl hujjatlardagi sahifa soniga ega: sertifikat 2, schedule 1, SoF 3
  * tasdiqlash emailining mavzusi va narx taqsimoti asl Tempcover xati bilan mos
Baza kerak emas — hammasi PolicyData va shablonlar ustida ishlaydi.
"""

import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pypdf import PdfReader  # noqa: E402

from app.services.pdf_service.models import PolicyData          # noqa: E402
from app.services.pdf_service.certificate import CertificateGenerator  # noqa: E402
from app.services.pdf_service.schedule import ScheduleGenerator        # noqa: E402
from app.services.pdf_service.statement import StatementGenerator      # noqa: E402
from app.services import email_service                          # noqa: E402

POLICY = PolicyData(
    policy_number="TCV-MOT-90075767", insured_name="Harry Potter", title="Mr",
    start_datetime="2026-09-11T21:18:00", end_datetime="2026-09-14T21:18:00",
    issued_at="2026-09-11T21:18:00",
    vehicle_registration="AB12", vehicle_make="MERCEDES-BENZ", vehicle_model="A-CLASS",
    price="20.00", value_range="£20001-25000",
    address_line_1="Flat 56", address_line_2="27 Albert", city="London", postcode="SE1 7AP",
    telephone="07555600809", email="driver@example.com", driver_dob="12 October 2000",
    driver_occupation="Driver", driver_sex="Male", agent_name="Tempcover Limited",
)

# Asl hujjatlardagi sahifa soni
EXPECTED_PAGES = {
    "certificate": (CertificateGenerator, 2),
    "schedule":    (ScheduleGenerator, 1),
    "statement":   (StatementGenerator, 3),
}


def check_pdfs() -> None:
    for name, (generator, pages) in EXPECTED_PAGES.items():
        data = generator(POLICY).generate()
        assert data[:4] == b"%PDF", f"{name}: PDF emas"
        # ReportLab fallback bir necha KB — WeasyPrint yiqilganini shundan bilamiz
        assert len(data) > 15_000, f"{name}: WeasyPrint fallback ishladi ({len(data)} bayt)"
        reader = PdfReader(io.BytesIO(data))
        got = len(reader.pages)
        assert got == pages, f"{name}: {got} sahifa, kutilgan {pages}"
        # Brauzer tabida UUID emas, hujjat nomi ko'rinadi
        title = (reader.metadata or {}).get("/Title", "")
        assert POLICY.policy_number in str(title), f"{name}: PDF sarlavhasi yo'q ({title!r})"
        print(f"  {name:12s} {pages} sahifa, {len(data):,} bayt — ok")


def check_email() -> None:
    captured = {}
    email_service._deliver = lambda to, name, subject, html, label, extra=None: (
        captured.__setitem__(label, (subject, html)) or "skipped")
    email_service.send_policy_confirmation_email(
        to_email="driver@example.com", driver_name="Harry Potter",
        policy_number="TCV-MOT-90075767",
        start_datetime="11 September 2026 at 21:18", end_datetime="14 September 2026 at 21:18",
        vehicle_reg="AB12", vehicle_make_model="MERCEDES-BENZ A-CLASS", price="20.00",
        verify_token="ci-token",
    )
    subject, html = captured["Policy confirmation"]
    assert subject == "Tempcover.com - Policy confirmation - TCV-MOT-90075767", subject
    # Asl xat: £20.00 = £10.80 + £1.30 (IPT 12%) + £7.90
    bd = email_service._calculate_breakdown(20.00)
    assert (bd["insurer_premium"], bd["ipt"], bd["fee"], bd["total"]) == ("10.80", "1.30", "7.90", "20.00"), bd
    for needle in ("£10.80", "£1.30", "£7.90", "72 hours", "View your policy documents", "/verifydetailspolicy?ref=TCV-MOT-90075767"):
        assert needle in html, f"emailda yo'q: {needle}"
    print("  email        mavzu va taqsimot — ok")


def check_timezone() -> None:
    """Agent kiritgan vaqt UK devor soati: yozda (BST) UTC dan 1 soat oldinda, qishda teng."""
    from datetime import datetime, timezone
    from app.services.policy_service import parse_dt, to_local, fmt_display
    summer = parse_dt("2026-09-14T08:15")
    winter = parse_dt("2026-01-14T08:15")
    assert summer == datetime(2026, 9, 14, 7, 15, tzinfo=timezone.utc), summer
    assert winter == datetime(2026, 1, 14, 8, 15, tzinfo=timezone.utc), winter
    assert to_local(summer).strftime("%H:%M") == "08:15"
    assert fmt_display(summer) == "Monday, 14 September 2026 at 8:15 AM", fmt_display(summer)
    print("  vaqt zonasi   BST/GMT — ok")


if __name__ == "__main__":
    print("Timezone:")
    check_timezone()
    print("PDF:")
    check_pdfs()
    print("Email:")
    check_email()
    print("smoke ok")
