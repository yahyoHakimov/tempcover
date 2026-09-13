# backend/app/services/pdf_service/service.py
import io
from pypdf import PdfWriter, PdfReader

from app.models.models import Policy
from app.services.branding import cover_label
from .models import PolicyData
from .certificate import CertificateGenerator
from .schedule import ScheduleGenerator
from .statement import StatementGenerator


class PDFService:

    @staticmethod
    def _to_policy_data(policy: Policy) -> PolicyData:
        """SQLAlchemy Policy ORM → PolicyData dataclass"""
        driver  = policy.driver
        vehicle = policy.vehicle

        # value_range ba'zan Enum, ba'zan string kelishi mumkin — ikkalasini ushlash
        vr = vehicle.value_range
        value_range = vr.value if hasattr(vr, 'value') else str(vr)

        # reason_for_issue ham xuddi shunday
        ri = policy.reason_for_issue
        reason_for_issue = ri.value if hasattr(ri, 'value') else str(ri)

        dob_str = ""
        if driver.date_of_birth:
            try:
                from datetime import date
                dob = driver.date_of_birth
                if isinstance(dob, date):
                    dob_str = dob.strftime("%d %B %Y")
                else:
                    dob_str = str(dob)
            except Exception:
                dob_str = str(driver.date_of_birth)

        return PolicyData(
            policy_number        = policy.policy_number,
            insured_name         = f"{driver.first_name} {driver.last_name}",
            start_datetime       = policy.start_datetime,
            end_datetime         = policy.end_datetime,
            issued_at            = policy.issued_at,
            vehicle_registration = vehicle.registration,
            vehicle_make         = vehicle.make,
            vehicle_model        = vehicle.model,
            value_range          = value_range,
            address_line_1       = driver.address_line_1,
            city                 = driver.city,
            postcode             = driver.postcode,
            price                = str(policy.price),
            compulsory_excess    = str(policy.compulsory_excess),
            voluntary_excess     = str(policy.voluntary_excess),
            reason_for_issue     = reason_for_issue,
            telephone            = getattr(driver, "mobile", "") or "",
            email                = getattr(driver, "email", "") or "",
            driver_dob           = dob_str,
            driver_licence_type  = "Full UK Licence",
            driver_occupation    = getattr(driver, "occupation", "") or "",
            policy_cover         = cover_label(policy.cover_type),
            agent_name           = policy.tenant.name if getattr(policy, "tenant", None) else "",
            version              = policy.version or 1,
        )

    @classmethod
    def certificate(cls, policy: Policy) -> bytes:
        return CertificateGenerator(cls._to_policy_data(policy)).generate()

    @classmethod
    def schedule(cls, policy: Policy) -> bytes:
        return ScheduleGenerator(cls._to_policy_data(policy)).generate()

    @classmethod
    def statement(cls, policy: Policy) -> bytes:
        return StatementGenerator(cls._to_policy_data(policy)).generate()

    @classmethod
    def combined(cls, policy: Policy) -> bytes:
        cert  = cls.certificate(policy)
        sched = cls.schedule(policy)
        writer = PdfWriter()
        for pdf_bytes in (cert, sched):
            for page in PdfReader(io.BytesIO(pdf_bytes)).pages:
                writer.add_page(page)
        out = io.BytesIO()
        writer.write(out)
        out.seek(0)
        return out.read()