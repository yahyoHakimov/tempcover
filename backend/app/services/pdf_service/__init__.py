"""
pdf_service — Motor Insurance PDF generation package.

Public API
----------
    from pdf_service import PDFService, PolicyData

    policy = PolicyData(
        policy_number="POL-2024-001",
        insured_name="Jane Smith",
        title="Ms",
        start_datetime="2024-04-01T09:00:00",
        end_datetime="2024-04-30T23:59:59",
        vehicle_registration="AB12 CDE",
        vehicle_make="BMW",
        vehicle_model="X5",
        value_range="£20,001 - £30,000",
        address_line_1="12 High Street",
        city="London",
        postcode="EC1A 1BB",
        price="87.50",
    )

    cert_bytes     = PDFService.certificate(policy)
    schedule_bytes = PDFService.schedule(policy)
    combined_bytes = PDFService.combined(policy)   # cert + schedule merged
"""

from .models import PolicyData
from .certificate import CertificateGenerator
from .schedule import ScheduleGenerator
from .service import PDFService

__all__ = ["PolicyData", "PDFService"]