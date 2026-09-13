"""
Email Service — Brevo transactional email.

Every send_* function returns one of:
    "sent"     delivered to Brevo
    "skipped"  BREVO_API_KEY is empty (dev mode) — the email is printed to the log instead
    "failed"   Brevo rejected it or the request errored
Only "sent" should mark a policy as emailed.
"""

from datetime import datetime

import httpx

from app.config import settings
from app.services.branding import documents_url

# Ranglar asl Tempcover xatidan olingan: banner/tugma to'q sariq, havolalar ko'k,
# matn qora, footer mayda matni kulrang.
BRAND      = "#F15A24"
LINK       = "#0B74D8"
TEXT       = "#000000"
MUTED      = "#4F4F53"
BORDER     = "#E5E7EB"
BRAND_DARK = "#000000"   # sarlavhalar va qalin matn
CONTENT_W  = 640   # asl xatda kontent 640px, banner esa to'liq kenglikda

EMAIL_DT = "%d %B %Y at %H:%M"   # format callers pass for start/end


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _calculate_breakdown(total: float) -> dict:
    """Premium breakdown shown to the driver (shares of the total)."""
    insurer_premium = round(total * 0.54, 2)
    ipt             = round(insurer_premium * 0.12, 2)
    fee             = round(total - insurer_premium - ipt, 2)
    return {
        "insurer_premium": f"{insurer_premium:.2f}",
        "ipt":             f"{ipt:.2f}",
        "fee":             f"{fee:.2f}",
        "discount":        "0.00",
        "total":           f"{total:.2f}",
    }


def _calculate_duration(start: str, end: str) -> str:
    try:
        diff  = datetime.strptime(end, EMAIL_DT) - datetime.strptime(start, EMAIL_DT)
        # Asl xat davomiylikni doim soatda ko'rsatadi ("72 hours"), kunga o'girmaydi.
        hours = int(diff.total_seconds() // 3600)
        return "1 hour" if hours == 1 else f"{hours} hours"
    except Exception:
        return ""


def _short(dt: str) -> str:
    try:
        return datetime.strptime(dt, EMAIL_DT).strftime("%d %B %Y %H:%M")
    except Exception:
        return dt


def _link(href: str, text: str) -> str:
    return f'<a href="{href}" style="color:{LINK};text-decoration:underline;">{text}</a>'


def _button(href: str, text: str) -> str:
    return (f'<div style="text-align:center;margin:26px 0 30px;">'
            f'<a href="{href}" style="display:inline-block;padding:16px 24px;background:{BRAND};color:#ffffff;'
            f'text-decoration:none;border-radius:4px;font-size:15px;font-weight:700;">{text}</a></div>')


def _site() -> str:
    """'tempcover.com' — sarlavha va havolalarda; banner/mavzuda bosh harf bilan."""
    return settings.SITE_NAME


def _site_cap() -> str:
    n = _site()
    return n[:1].upper() + n[1:]


def _legal_footer_html() -> str:
    """Asl xatdagi tartib: kichik wordmark, maxfiylik ogohlantirishi, kompaniya bloki
    (bosh harflar, markazda), copyright, FCA/underwriter qatorlari, Terms | Privacy.
    Har bir qator sozlamalardan; bo'sh qiymat — qator chiqmaydi."""
    s = settings
    year = datetime.now().year
    small = f"margin:0 0 12px;font-size:11px;line-height:1.55;color:{MUTED};text-align:center;"

    company_block = [s.COMPANY_LEGAL_NAME.upper()]
    if s.COMPANY_REG_NO:
        company_block.append(f"REGISTERED IN ENGLAND NO.{s.COMPANY_REG_NO}")
    if s.REGISTERED_OFFICE:
        company_block.append(f"REGISTERED OFFICE: {s.REGISTERED_OFFICE.upper()}")

    reg_lines = []
    if s.FCA_FRN:
        reg_lines.append(
            f"{s.COMPANY_LEGAL_NAME} (FRN {s.FCA_FRN}) is authorised and regulated by the Financial Conduct Authority. "
            "You can check this on the Financial Services Register.")
    if s.UNDERWRITER_NAME:
        frn = f" (FRN {s.UNDERWRITER_FRN})" if s.UNDERWRITER_FRN else ""
        reg_lines.append(
            f"{s.TRADING_NAME} policies are underwritten by {s.UNDERWRITER_NAME}{frn}, "
            "which is authorised and regulated by the Financial Conduct Authority.")

    return f"""
      <p style="margin:26px 0 14px;font-size:15px;font-weight:700;color:{TEXT};">{_site().split('.')[0]}</p>
      <p style="margin:0 0 20px;font-size:11px;line-height:1.55;color:{MUTED};">
        IMPORTANT CONFIDENTIALITY NOTICE: this email and the information it contains may be confidential, legally
        privileged and protected by law. If you have received this email in error, please notify us immediately and
        delete it from your system. Any unauthorised copying, disclosure or distribution of the material in this email
        is strictly forbidden.
      </p>
      <p style="margin:0 0 14px;font-size:12px;line-height:1.6;font-weight:700;color:{TEXT};text-align:center;">
        {"<br>".join(company_block)}
      </p>
      <p style="{small}">© Copyright {year} {s.COMPANY_LEGAL_NAME}. All rights reserved.</p>
      {"".join(f'<p style="{small}">{l}</p>' for l in reg_lines)}
      <p style="margin:0 0 8px;font-size:12px;color:{MUTED};text-align:center;">
        {_link(f"{s.APP_URL}/terms", "Terms")} &nbsp;|&nbsp; {_link(f"{s.APP_URL}/privacy", "Privacy")}
      </p>
    """


def _shell(title: str, banner: str, body: str) -> str:
    """Asl xat: to'liq kenglikdagi to'q sariq banner, so'ng 640px markazlashgan kontent —
    logotip chapda, Trustpilot bloki o'ngda. Karta/soya/qora footer yo'q."""
    app = settings.APP_URL
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
</head>
<body style="margin:0;padding:0;background:#ffffff;font-family:Arial,Helvetica,sans-serif;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#ffffff;">
    <tr><td style="background:{BRAND};padding:9px 16px;color:#ffffff;font-size:15px;font-weight:700;">{banner}</td></tr>
    <tr><td align="center" style="padding:0 16px;">
      <table role="presentation" width="{CONTENT_W}" cellpadding="0" cellspacing="0" style="max-width:{CONTENT_W}px;width:100%;">
        <tr><td style="padding:26px 0 24px;">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>
            <td style="vertical-align:middle;">
              <img src="{app}/tempcover-logo-dark.png" alt="{settings.TRADING_NAME}" width="179"
                   style="display:block;height:34px;width:auto;border:0;" />
            </td>
            <td align="right" style="vertical-align:middle;">
              <img src="{app}/trustpilot.png" alt="Trustpilot" width="158"
                   style="display:block;width:158px;height:auto;border:0;" />
            </td>
          </tr></table>
        </td></tr>
        <tr><td style="font-size:15px;line-height:1.6;color:{TEXT};">
          {body}
          {_legal_footer_html()}
        </td></tr>
      </table>
    </td></tr>
  </table>
  <div style="height:24px;"></div>
</body>
</html>"""


def _deliver(to_email: str, to_name: str, subject: str, html: str, log_label: str, log_extra: dict | None = None) -> str:
    if not settings.BREVO_API_KEY:
        print(f"\n{'=' * 50}\n[DEV EMAIL] {log_label}\n[DEV EMAIL] To:      {to_email}\n[DEV EMAIL] Subject: {subject}")
        for k, v in (log_extra or {}).items():
            print(f"[DEV EMAIL] {k}: {v}")
        print(f"{'=' * 50}\n")
        return "skipped"
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(
                "https://api.brevo.com/v3/smtp/email",
                json={
                    "sender":      {"name": settings.FROM_NAME, "email": settings.FROM_EMAIL},
                    "to":          [{"email": to_email, "name": to_name}],
                    "subject":     subject,
                    "htmlContent": html,
                },
                headers={"api-key": settings.BREVO_API_KEY, "Content-Type": "application/json"},
            )
            resp.raise_for_status()
            return "sent"
    except httpx.HTTPStatusError as e:
        print(f"[EMAIL ERROR] HTTP {e.response.status_code}: {e.response.text}")
        return "failed"
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return "failed"


# ─────────────────────────────────────────────────────────────────────────────
# Policy confirmation / update
# ─────────────────────────────────────────────────────────────────────────────

def _policy_summary_html(policy_number, driver_name, vehicle_make_model, vehicle_reg, duration, start, end, price) -> str:
    bd = _calculate_breakdown(float(price))
    s  = settings

    # Asl xat: yorliq qalin qora, qiymat oddiy qora; transport qiymatlari ko'k.
    def row(label, value, blue=False):
        color = LINK if blue else TEXT
        return (f'<tr><td style="padding:2px 0;width:44%;font-weight:700;color:{TEXT};">{label}</td>'
                f'<td style="padding:2px 0;color:{color};">{value}</td></tr>')

    def cost(label, value):
        return (f'<tr><td style="padding:2px 0;font-weight:700;color:{TEXT};">{label}</td>'
                f'<td style="padding:2px 0;text-align:right;color:{TEXT};">{value}</td></tr>')

    insurer = f"{s.UNDERWRITER_NAME} insurer premium:" if s.UNDERWRITER_NAME else "Insurer premium:"
    charged = _link(f"{s.APP_URL}/terms", f"£{bd['total']}")

    return f"""
      <h3 style="margin:0 0 12px;font-size:16px;font-weight:700;color:{TEXT};">Policy summary</h3>
      <table style="width:100%;border-collapse:collapse;font-size:15px;line-height:1.5;">
        {row("Policy number:", policy_number)}
        {row("Policy holder:", driver_name)}
        {row("Vehicle type:", vehicle_make_model, blue=True)}
        {row("Vehicle registration:", vehicle_reg, blue=True)}
        {row("Duration:", duration)}
        {row("Start date/time:", _short(start))}
        {row("End date/time:", _short(end))}
      </table>

      <p style="margin:22px 0 12px;font-size:15px;font-weight:700;color:{TEXT};line-height:1.6;">
        You have been charged {charged} and a breakdown of the cost is below:
      </p>
      <table style="width:100%;border-collapse:collapse;font-size:15px;line-height:1.5;">
        {cost(insurer, f"£{bd['insurer_premium']}")}
        {cost("Insurance premium tax:", f"£{bd['ipt']}")}
        {cost(f"{s.TRADING_NAME} Fee:", f"£{bd['fee']}")}
        {cost("Campaign Discount:", f"-£{bd['discount']}")}
        {cost("Total charged:", f"£{bd['total']}")}
      </table>
    """


def _mid_html() -> str:
    p = f"margin:0 0 16px;font-size:15px;color:{TEXT};line-height:1.6;"
    return f"""
      <h3 style="margin:28px 0 12px;font-size:16px;font-weight:700;color:{LINK};">Updating the MID</h3>
      <p style="{p}">
        Your insurance details will shortly be passed to the
        {_link("https://enquiry.navigate.mib.org.uk/checkyourvehicle", "Motor Insurance Database (MID)")}
        within the timescales required by the MID. However, due to the short-term nature of your policy,
        it is possible your policy may have expired before the details are loaded into the database.
      </p>
      <p style="{p}">
        We recommend that you <strong>print your insurance certificate</strong> and have this with you whilst you drive
        the vehicle as this remains valid proof of your insurance and legal entitlement to drive the vehicle.
        If you need to get in touch with us, please {_link(f"{settings.APP_URL}/contact", "Contact Us")}.
      </p>
      <p style="{p}">We hope to see you again soon,</p>
      <p style="{p}">
        You are receiving this email as part of our quote service. This service does not relate to the marketing
        communication preferences you set when obtaining a quote.
      </p>
    """


def send_policy_confirmation_email(
    to_email: str,
    driver_name: str,
    policy_number: str,
    start_datetime: str,
    end_datetime: str,
    vehicle_reg: str,
    vehicle_make_model: str,
    price: str,
    verify_token: str,
    updated: bool = False,
    version: int = 1,
) -> str:
    """Confirmation for a new policy, or the re-issued documents after a mid-term adjustment."""
    site     = _site()
    docs     = documents_url(policy_number, verify_token)
    duration = _calculate_duration(start_datetime, end_datetime)
    p        = f"margin:0 0 16px;font-size:15px;color:{TEXT};line-height:1.6;"

    if updated:
        banner  = f"{_site_cap()} policy update"
        subject = f"{_site_cap()} - Policy updated - {policy_number}"
        intro   = f"""
          <h2 style="margin:0 0 6px;font-size:20px;font-weight:700;color:{TEXT};text-align:center;">Your policy has been updated</h2>
          <p style="margin:0 0 24px;font-size:14px;color:{MUTED};text-align:center;">Policy {policy_number} · version {version}</p>
          <p style="{p}">Hi {driver_name},</p>
          <p style="{p}">
            The details of your temporary insurance policy have changed. Your documents have been re-issued and the
            previous versions are no longer valid. Please review the summary below and download the updated documents.
          </p>
        """
    else:
        banner  = f"{_site_cap()} policy confirmation"
        subject = f"{_site_cap()} - Policy confirmation - {policy_number}"
        intro   = f"""
          <h2 style="margin:0 0 14px;font-size:20px;font-weight:700;color:{TEXT};text-align:center;">
            Thanks for choosing <a href="{settings.APP_URL}" style="color:{LINK};text-decoration:none;">{site}</a>
          </h2>
          <p style="margin:0 0 22px;font-size:18px;font-weight:700;color:{TEXT};text-align:center;">
            Your temporary insurance is all ready to go!
          </p>
          <p style="{p}">Hi {driver_name},</p>
          <p style="{p}">
            You can relax now, everything is taken care of. Your temporary insurance policy is in place and will
            begin at the time you selected.
          </p>
          <p style="{p}">
            Check out the summary of your policy and a link to view and print your policy documents below.
          </p>
          <p style="{p}">
            Should you need to make a claim at any point, please {_link(f"{settings.APP_URL}/contact", "Click here")} for more information.
          </p>
          <p style="{p}">
            Thanks again for choosing {_link(settings.APP_URL, site)} for your temporary insurance needs - we hope to
            see you again soon.
          </p>
          <p style="margin:0 0 14px;font-size:13px;color:{TEXT};font-style:italic;text-align:center;line-height:1.6;">
            This policy meets the Demands and Needs of a customer who wishes to insure a vehicle for a short period.
          </p>
          <p style="margin:0;font-size:13px;color:{TEXT};text-align:center;">
            Our Customer Terms of Business can be found {_link(f"{settings.APP_URL}/terms", "here")}.
          </p>
        """

    body = (intro
            + _button(docs, "View your policy documents")
            + _policy_summary_html(policy_number, driver_name, vehicle_make_model, vehicle_reg, duration, start_datetime, end_datetime, price)
            + _mid_html())

    return _deliver(to_email, driver_name, subject, _shell(subject, banner, body),
                    "Policy update" if updated else "Policy confirmation",
                    {"Policy": policy_number, "Documents": docs})


# ─────────────────────────────────────────────────────────────────────────────
# Cancellation
# ─────────────────────────────────────────────────────────────────────────────

def send_policy_cancellation_email(to_email: str, driver_name: str, policy_number: str, reason: str | None = None) -> str:
    brand   = settings.TRADING_NAME
    subject = f"{brand} - Policy cancelled - {policy_number}"
    reason_html = (f'<p style="margin:0 0 12px;font-size:14px;color:{TEXT};line-height:1.6;">Reason recorded: <strong>{reason}</strong></p>'
                   if reason else "")
    body = f"""
      <h2 style="margin:0 0 18px;font-size:18px;font-weight:700;color:{BRAND_DARK};text-align:center;">Your policy has been cancelled</h2>
      <p style="margin:0 0 12px;font-size:14px;color:{TEXT};">Hi {driver_name},</p>
      <p style="margin:0 0 12px;font-size:14px;color:{TEXT};line-height:1.6;">
        We're writing to confirm that your {brand} policy <strong style="color:{BRAND_DARK};">{policy_number}</strong>
        has been cancelled and is no longer in force. You are not insured under this policy from now on, and the
        documents previously issued for it are no longer valid.
      </p>
      {reason_html}
      <p style="margin:0 0 12px;font-size:14px;color:{TEXT};line-height:1.6;">
        If this cancellation was unexpected or you have any questions, please contact us at
        {_link(f"mailto:{settings.SUPPORT_EMAIL}", settings.SUPPORT_EMAIL)} and we'll get back to you within one working day.
      </p>
    """
    return _deliver(to_email, driver_name, subject, _shell(subject, f"{brand} policy cancellation", body),
                    "Cancellation", {"Policy": policy_number, "Reason": reason or "-"})


# ─────────────────────────────────────────────────────────────────────────────
# Expiry reminder (driver) and expiring-soon digest (agent)
# ─────────────────────────────────────────────────────────────────────────────

def send_expiry_reminder_email(to_email: str, driver_name: str, policy_number: str, vehicle_reg: str,
                               end_display: str, verify_token: str) -> str:
    brand   = settings.TRADING_NAME
    subject = f"{brand} - Your policy {policy_number} ends soon"
    docs    = documents_url(policy_number, verify_token)
    body = f"""
      <h2 style="margin:0 0 18px;font-size:18px;font-weight:700;color:{BRAND_DARK};text-align:center;">Your temporary insurance ends soon</h2>
      <p style="margin:0 0 12px;font-size:14px;color:{TEXT};">Hi {driver_name},</p>
      <p style="margin:0 0 12px;font-size:14px;color:{TEXT};line-height:1.6;">
        A quick reminder that your policy <strong style="color:{BRAND_DARK};">{policy_number}</strong> for vehicle
        <strong>{vehicle_reg}</strong> ends on <strong>{end_display}</strong>. After that time you will no longer be
        insured under this policy.
      </p>
      <p style="margin:0 0 12px;font-size:14px;color:{TEXT};line-height:1.6;">
        If you need cover beyond this time, please arrange a new policy before it ends. Your current documents are
        available below.
      </p>
      {_button(docs, "View your policy documents")}
    """
    return _deliver(to_email, driver_name, subject, _shell(subject, f"{brand} policy reminder", body),
                    "Expiry reminder", {"Policy": policy_number, "Ends": end_display})


def send_agent_expiry_digest_email(to_email: str, agent_name: str, rows: list[dict], days_ahead: int) -> str:
    """rows: [{policy_number, driver_name, vehicle_reg, end_display}]"""
    brand   = settings.TRADING_NAME
    subject = f"{brand} - {len(rows)} {'policy' if len(rows) == 1 else 'policies'} expiring in the next {days_ahead} days"
    trs = "".join(
        f'<tr>'
        f'<td style="padding:8px 6px;border-bottom:1px solid #F3F4F6;font-weight:700;color:{BRAND_DARK};">{r["policy_number"]}</td>'
        f'<td style="padding:8px 6px;border-bottom:1px solid #F3F4F6;color:{TEXT};">{r["driver_name"]}</td>'
        f'<td style="padding:8px 6px;border-bottom:1px solid #F3F4F6;color:{TEXT};">{r["vehicle_reg"]}</td>'
        f'<td style="padding:8px 6px;border-bottom:1px solid #F3F4F6;color:{TEXT};white-space:nowrap;">{r["end_display"]}</td>'
        f'</tr>' for r in rows)
    body = f"""
      <h2 style="margin:0 0 18px;font-size:18px;font-weight:700;color:{BRAND_DARK};">Policies expiring soon</h2>
      <p style="margin:0 0 16px;font-size:14px;color:{TEXT};line-height:1.6;">
        Hi {agent_name}, these policies on your account end within the next {days_ahead} days:
      </p>
      <table style="width:100%;border-collapse:collapse;font-size:13px;">
        <tr>
          <th align="left" style="padding:6px;color:{MUTED};font-size:11px;text-transform:uppercase;letter-spacing:.5px;">Policy</th>
          <th align="left" style="padding:6px;color:{MUTED};font-size:11px;text-transform:uppercase;letter-spacing:.5px;">Driver</th>
          <th align="left" style="padding:6px;color:{MUTED};font-size:11px;text-transform:uppercase;letter-spacing:.5px;">Vehicle</th>
          <th align="left" style="padding:6px;color:{MUTED};font-size:11px;text-transform:uppercase;letter-spacing:.5px;">Ends</th>
        </tr>
        {trs}
      </table>
      {_button(f"{settings.APP_URL}/admin/policies?filter=expiringweek", "Open expiring policies")}
    """
    return _deliver(to_email, agent_name, subject, _shell(subject, f"{brand} agent digest", body),
                    "Agent digest", {"Agent": agent_name, "Policies": len(rows)})
