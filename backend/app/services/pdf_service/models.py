"""
Data models for PDF generation service.
Uses dataclasses + manual validation — no third-party deps beyond reportlab/pypdf.
Compatible with Pydantic v1/v2 if available, but not required.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


def _to_dt(value: str | datetime | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, str):
        return datetime.fromisoformat(value)
    return value


@dataclass
class PolicyData:
    # ── Required ────────────────────────────────────────────────────────
    policy_number:        str
    insured_name:         str
    start_datetime:       datetime | str
    end_datetime:         datetime | str
    vehicle_registration: str
    vehicle_make:         str
    vehicle_model:        str
    price:                str

    # ── Optional ────────────────────────────────────────────────────────
    title:              str = ""
    issued_at:          datetime | str | None = None
    value_range:        str = "N/A"
    address_line_1:     str = ""
    city:               str = ""
    postcode:           str = ""
    compulsory_excess:  str = "500.00"
    voluntary_excess:   str = "0.00"
    reason_for_issue:   str = "New Business"
    agent_name:         str = ""
    version:            int = 1

    # ── Statement of Fact fields ─────────────────────────────────────────
    telephone:          str = ""
    email:              str = ""
    policy_cover:       str = "Fully Comprehensive"
    number_of_drivers:  str = "1"
    driver_sex:         str = "—"
    driver_dob:         str = ""
    driver_licence_type: str = "Full UK Licence"
    driver_occupation:  str = ""

    def __post_init__(self) -> None:
        # Coerce strings → datetime
        self.start_datetime = _to_dt(self.start_datetime)   # type: ignore[assignment]
        self.end_datetime   = _to_dt(self.end_datetime)     # type: ignore[assignment]
        self.issued_at      = _to_dt(self.issued_at) or datetime.now()

        # Basic validation
        if not self.policy_number:
            raise ValueError("policy_number is required")
        if not self.insured_name:
            raise ValueError("insured_name is required")
        if self.start_datetime >= self.end_datetime:           # type: ignore[operator]
            raise ValueError("start_datetime must be before end_datetime")

    # ── Computed properties ─────────────────────────────────────────────

    @property
    def insured_display(self) -> str:
        return f"{self.title} {self.insured_name}".strip()

    @property
    def make_model(self) -> str:
        return f"{self.vehicle_make}, {self.vehicle_model}"

    @property
    def total_excess(self) -> str:
        try:
            total = float(self.compulsory_excess) + float(self.voluntary_excess)
            return f"{total:.2f}"
        except ValueError:
            return self.compulsory_excess

    # ── dict → PolicyData convenience constructor ────────────────────────

    @classmethod
    def from_dict(cls, data: dict) -> "PolicyData":
        """Allow passing raw dicts (e.g. from FastAPI request body)."""
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        return cls(**{k: v for k, v in data.items() if k in known})