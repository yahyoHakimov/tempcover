"""
Brand / legal text helpers — single source for what emails and PDFs print about the company.
Every line is driven by settings; blank settings mean the line is left out.
"""

from app.config import settings

COVER_LABELS = {
    "fully_comprehensive":    "Fully Comprehensive",
    "third_party_fire_theft": "Third Party, Fire & Theft",
    "third_party_only":       "Third Party Only",
}


def cover_label(cover_type) -> str:
    key = getattr(cover_type, "value", cover_type)
    return COVER_LABELS.get(str(key), "Fully Comprehensive")


def site_domain() -> str:
    return settings.APP_URL.split("://", 1)[-1].split("/", 1)[0]


def documents_url(policy_number: str, verify_token: str) -> str:
    """One-click link from the email to the driver's documents page."""
    return f"{settings.APP_URL}/verifydetailspolicy/complete/{policy_number}?t={verify_token}"


def legal_lines() -> list[str]:
    """Regulatory footer lines, built only from configured values."""
    s = settings
    lines = [f"{s.TRADING_NAME} and {site_domain()} are trading names of {s.COMPANY_LEGAL_NAME}."]

    if s.UNDERWRITER_NAME:
        frn = f" (FRN {s.UNDERWRITER_FRN})" if s.UNDERWRITER_FRN else ""
        lines.append(
            f"{s.TRADING_NAME} policies are underwritten by {s.UNDERWRITER_NAME}{frn}, "
            "which is authorised and regulated by the Financial Conduct Authority."
        )
    else:
        lines.append("Policies are underwritten by the insurer named in your policy schedule.")

    if s.COMPANY_REG_NO:
        office = f", registered office {s.REGISTERED_OFFICE}" if s.REGISTERED_OFFICE else ""
        lines.append(f"{s.COMPANY_LEGAL_NAME} is registered in England and Wales, company number {s.COMPANY_REG_NO}{office}.")

    if s.FCA_FRN:
        lines.append(
            f"{s.COMPANY_LEGAL_NAME} is authorised and regulated by the Financial Conduct Authority (FRN {s.FCA_FRN}). "
            "You can check this on the Financial Services Register."
        )
    return lines


def legal_footer_text() -> str:
    return " ".join(legal_lines())


def insurer_info_text() -> str:
    """'Insurer Information' box on the policy schedule."""
    s = settings
    if s.UNDERWRITER_NAME:
        frn = f" (FRN {s.UNDERWRITER_FRN})" if s.UNDERWRITER_FRN else ""
        text = (f"Cover has been issued and arranged by {s.COMPANY_LEGAL_NAME} under authority granted by "
                f"{s.UNDERWRITER_NAME}{frn}, which is authorised and regulated by the Financial Conduct Authority.")
    else:
        text = f"Cover has been issued and arranged by {s.COMPANY_LEGAL_NAME}. The insurer is shown on your Certificate of Motor Insurance."
    if s.FCA_FRN:
        text += f" {s.COMPANY_LEGAL_NAME} is authorised and regulated by the Financial Conduct Authority under FRN {s.FCA_FRN}."
    return text
