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
from app.services.branding import documents_url, legal_lines

BRAND      = "#FF5100"
BRAND_DARK = "#1F2937"
TEXT       = "#374151"
MUTED      = "#6B7280"
BORDER     = "#E5E7EB"

EMAIL_DT = "%d %B %Y at %H:%M"   # format callers pass for start/end


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _calculate_breakdown(total: float) -> dict:
    """Premium breakdown shown to the driver (shares of the total)."""
    insurer_premium = round(total * 0.68, 2)
    ipt             = round(insurer_premium * 0.20, 2)
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
        hours = int(diff.total_seconds() // 3600)
        if hours < 24:
            return f"{hours} hours"
        days, rem = divmod(hours, 24)
        if rem:
            return f"{hours} hours"
        return f"{days} day" if days == 1 else f"{days} days"
    except Exception:
        return ""


def _short(dt: str) -> str:
    try:
        return datetime.strptime(dt, EMAIL_DT).strftime("%d %B %Y %H:%M")
    except Exception:
        return dt


def _link(href: str, text: str) -> str:
    return f'<a href="{href}" style="color:{BRAND};text-decoration:none;font-weight:600;">{text}</a>'


def _button(href: str, text: str) -> str:
    return (f'<div style="text-align:center;margin:28px 0;">'
            f'<a href="{href}" style="display:inline-block;padding:14px 36px;background:{BRAND};color:#ffffff;'
            f'text-decoration:none;border-radius:8px;font-size:15px;font-weight:700;letter-spacing:0.3px;">{text}</a></div>')


def _legal_footer_html() -> str:
    year  = datetime.now().year
    lines = "".join(f'<p style="margin:0 0 8px;font-size:11px;color:{MUTED};line-height:1.7;">{l}</p>' for l in legal_lines())
    return f"""
      <hr style="border:none;border-top:1px solid {BORDER};margin:24px 0;">
      <p style="margin:0 0 10px;font-size:11px;color:{MUTED};line-height:1.7;">
        <strong style="color:{TEXT};">Important confidentiality notice:</strong> this email and the information it contains
        may be confidential. If you have received this email in error, please notify us immediately and delete it from your system.
      </p>
      <p style="margin:0 0 10px;font-size:11px;color:{MUTED};line-height:1.7;">
        You are receiving this email as part of our policy service. This does not relate to any marketing
        communication preferences you may have set.
      </p>
      {lines}
      <p style="margin:12px 0 0;font-size:11px;color:#9CA3AF;line-height:1.7;">
        © {year} {settings.COMPANY_LEGAL_NAME}. All rights reserved. &nbsp;|&nbsp;
        {_link(f"{settings.APP_URL}/terms", "Terms")} &nbsp;|&nbsp;
        {_link(f"{settings.APP_URL}/privacy", "Privacy")} &nbsp;|&nbsp;
        {_link(f"{settings.APP_URL}/contact", "Contact us")}
      </p>
    """


def _shell(title: str, banner: str, body: str) -> str:
    """Common chrome: orange banner with the email title, white header with logo, dark footer."""
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
</head>
<body style="margin:0;padding:0;background:#F3F4F6;font-family:Arial,Helvetica,sans-serif;">
  <div style="max-width:640px;margin:24px auto;background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.06);">
    <div style="background:{BRAND};padding:12px 24px;color:#ffffff;font-size:15px;font-weight:700;">{banner}</div>
    <div style="padding:24px 32px 8px;border-bottom:1px solid {BORDER};">
      <img src="{settings.APP_URL}/tempcover-logo.png" alt="{settings.TRADING_NAME}" style="height:34px;max-width:200px;object-fit:contain;" />
    </div>
    <div style="padding:28px 32px 32px;">
      {body}
      {_legal_footer_html()}
    </div>
    <div style="background:{BRAND_DARK};padding:20px 32px;text-align:center;">
      <img src="{settings.APP_URL}/tempcover-logo-white.png" alt="{settings.TRADING_NAME}" style="height:22px;object-fit:contain;" />
    </div>
  </div>
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

    def row(label, value, accent=False, strong=False):
        color  = BRAND if accent else BRAND_DARK
        weight = "700" if (strong or accent) else "400"
        return (f'<tr><td style="padding:7px 0;color:{MUTED};width:45%;font-weight:600;">{label}</td>'
                f'<td style="padding:7px 0;color:{color};font-weight:{weight};">{value}</td></tr>')

    def cost(label, value, total=False):
        w = "700" if total else "400"
        b = "" if total else "border-bottom:1px solid #F3F4F6;"
        return (f'<tr><td style="padding:6px 0;color:{TEXT};font-weight:600;{b}">{label}</td>'
                f'<td style="padding:6px 0;color:{BRAND_DARK};text-align:right;font-weight:{w};{b}">{value}</td></tr>')

    return f"""
      <h3 style="margin:0 0 14px;font-size:15px;font-weight:700;color:{BRAND_DARK};">Policy summary</h3>
      <table style="width:100%;border-collapse:collapse;font-size:14px;">
        {row("Policy number:", policy_number, strong=True)}
        {row("Policy holder:", driver_name)}
        {row("Vehicle type:", vehicle_make_model, accent=True)}
        {row("Vehicle registration:", vehicle_reg, accent=True)}
        {row("Duration:", duration)}
        {row("Start date/time:", _short(start))}
        {row("End date/time:", _short(end))}
      </table>

      <p style="margin:20px 0 12px;font-size:14px;color:{TEXT};line-height:1.6;">
        You have been charged <strong style="color:{BRAND};">£{bd['total']}</strong> and a breakdown of the cost is below:
      </p>
      <table style="width:100%;border-collapse:collapse;font-size:14px;">
        {cost("Insurer premium:", f"£{bd['insurer_premium']}")}
        {cost("Insurance premium tax:", f"£{bd['ipt']}")}
        {cost(f"{settings.TRADING_NAME} fee:", f"£{bd['fee']}")}
        {cost("Campaign discount:", f"-£{bd['discount']}")}
        {cost("Total charged:", f"£{bd['total']}", total=True)}
      </table>
    """


def _mid_html() -> str:
    return f"""
      <h3 style="margin:28px 0 10px;font-size:15px;font-weight:700;color:{BRAND};">Updating the MID</h3>
      <p style="margin:0 0 12px;font-size:13px;color:{TEXT};line-height:1.6;">
        Your insurance details will be passed to the
        {_link("https://enquiry.navigate.mib.org.uk/checkyourvehicle", "Motor Insurance Database (MID)")}
        within the timescales required by the MID. However, due to the short-term nature of your policy,
        it is possible your policy may have expired before the details are loaded into the database.
      </p>
      <p style="margin:0 0 12px;font-size:13px;color:{TEXT};line-height:1.6;">
        We recommend that you <strong>print your insurance certificate</strong> and have this with you whilst you drive
        the vehicle, as this remains valid proof of your insurance and legal entitlement to drive the vehicle.
        If you need to get in touch with us, please {_link(f"mailto:{settings.SUPPORT_EMAIL}", "contact us")}.
      </p>
      <p style="margin:0 0 4px;font-size:13px;color:{TEXT};line-height:1.6;">We hope to see you again soon.</p>
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
    brand    = settings.TRADING_NAME
    docs     = documents_url(policy_number, verify_token)
    duration = _calculate_duration(start_datetime, end_datetime)

    if updated:
        banner  = f"{brand} policy update"
        subject = f"{brand} - Policy updated - {policy_number}"
        intro   = f"""
          <h2 style="margin:0 0 6px;font-size:18px;font-weight:700;color:{BRAND_DARK};text-align:center;">Your policy has been updated</h2>
          <p style="margin:0 0 24px;font-size:14px;color:{MUTED};text-align:center;">Policy {policy_number} · version {version}</p>
          <p style="margin:0 0 12px;font-size:14px;color:{TEXT};">Hi {driver_name},</p>
          <p style="margin:0 0 12px;font-size:14px;color:{TEXT};line-height:1.6;">
            The details of your temporary insurance policy have changed. Your documents have been re-issued and the
            previous versions are no longer valid. Please review the summary below and download the updated documents.
          </p>
        """
    else:
        banner  = f"{brand} policy confirmation"
        subject = f"{brand} - Policy confirmation - {policy_number}"
        intro   = f"""
          <h2 style="margin:0 0 6px;font-size:18px;font-weight:700;color:{BRAND_DARK};text-align:center;">
            Thanks for choosing {_link(settings.APP_URL, brand)}
          </h2>
          <p style="margin:0 0 24px;font-size:16px;font-weight:700;color:{BRAND_DARK};text-align:center;">
            Your temporary insurance is all ready to go!
          </p>
          <p style="margin:0 0 12px;font-size:14px;color:{TEXT};">Hi {driver_name},</p>
          <p style="margin:0 0 12px;font-size:14px;color:{TEXT};line-height:1.6;">
            You can relax now, everything is taken care of. Your temporary insurance policy is in place and will
            begin at the time you selected.
          </p>
          <p style="margin:0 0 12px;font-size:14px;color:{TEXT};line-height:1.6;">
            Check out the summary of your policy and a link to view and print your policy documents below.
          </p>
          <p style="margin:0 0 12px;font-size:14px;color:{TEXT};line-height:1.6;">
            Should you need to make a claim at any point, please {_link(f"{settings.APP_URL}/contact", "contact us")} for more information.
          </p>
          <p style="margin:0 0 16px;font-size:14px;color:{TEXT};line-height:1.6;">
            Thanks again for choosing {brand} for your temporary insurance needs - we hope to see you again soon.
          </p>
          <p style="margin:0 0 6px;font-size:13px;color:{MUTED};font-style:italic;text-align:center;line-height:1.6;">
            This policy meets the demands and needs of a customer who wishes to insure a vehicle for a short period.
          </p>
          <p style="margin:0 0 4px;font-size:13px;color:{MUTED};text-align:center;">
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
