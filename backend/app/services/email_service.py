"""
Email Service — Brevo transactional email
Policy confirmation and cancellation emails.
With BREVO_API_KEY empty, emails are printed to the log instead (dev mode).
"""

from datetime import datetime

import httpx

from app.config import settings

BRAND      = "#FF5100"   # TempCover orange
BRAND_DARK = "#1F2937"   # headings / footer
TEXT       = "#374151"
MUTED      = "#6B7280"
BORDER     = "#E5E7EB"


def _calculate_breakdown(total: float) -> dict:
    """Premium breakdown shown in the confirmation email (percentages of the total)."""
    insurer_premium = round(total * 0.68, 2)
    ipt             = round(insurer_premium * 0.20, 2)
    admin_fee       = round(total * 0.12, 2)
    return {
        "insurer_premium": f"{insurer_premium:.2f}",
        "ipt":             f"{ipt:.2f}",
        "admin_fee":       f"{admin_fee:.2f}",
        "discount":        "0.00",
        "total":           f"{total:.2f}",
    }


def _calculate_duration(start: str, end: str) -> str:
    try:
        fmt = "%d %B %Y at %H:%M"
        diff = datetime.strptime(end, fmt) - datetime.strptime(start, fmt)
        hours = int(diff.total_seconds() / 3600)
        if hours < 24:
            return f"{hours} hours"
        days, remaining = divmod(hours, 24)
        return f"{days} days {remaining} hours" if remaining else f"{days} days"
    except Exception:
        return ""


def _short(dt: str) -> str:
    try:
        return datetime.strptime(dt, "%d %B %Y at %H:%M").strftime("%d %B %Y %H:%M")
    except Exception:
        return dt


def _shell(title: str, body: str) -> str:
    """Common email chrome: orange top bar, white header with logo, dark footer."""
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
</head>
<body style="margin:0;padding:0;background:#F3F4F6;font-family:Arial,Helvetica,sans-serif;">
  <div style="background:{BRAND};height:6px;width:100%;"></div>
  <div style="max-width:620px;margin:24px auto;background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.06);">
    <div style="padding:26px 32px;text-align:center;border-bottom:1px solid {BORDER};">
      <img src="{settings.APP_URL}/tempcover-logo.png" alt="TempCover" style="height:36px;max-width:200px;object-fit:contain;" />
    </div>
    <div style="padding:32px;">
      {body}
    </div>
    <div style="background:{BRAND_DARK};padding:22px 32px;text-align:center;">
      <img src="{settings.APP_URL}/tempcover-logo-white.png" alt="TempCover" style="height:22px;object-fit:contain;margin-bottom:8px;" />
      <div style="font-size:11px;color:rgba(255,255,255,0.55);line-height:1.6;">
        © {datetime.now().year} TempCover. All rights reserved.<br>
        Authorised and regulated by the Financial Conduct Authority.
      </div>
    </div>
  </div>
  <div style="height:24px;"></div>
</body>
</html>"""


def _build_email_html(
    driver_name: str,
    policy_number: str,
    start_datetime: str,
    end_datetime: str,
    vehicle_reg: str,
    vehicle_make_model: str,
    price: str,
    verify_url: str,
) -> str:
    bd       = _calculate_breakdown(float(price))
    duration = _calculate_duration(start_datetime, end_datetime)
    link     = f'style="color:{BRAND};text-decoration:none;font-weight:600;"'

    def row(label, value, strong=False, accent=False):
        color  = BRAND if accent else BRAND_DARK
        weight = "700" if strong or accent else "400"
        return (f'<tr><td style="padding:7px 0;color:{MUTED};width:45%;font-weight:600;">{label}</td>'
                f'<td style="padding:7px 0;color:{color};font-weight:{weight};">{value}</td></tr>')

    def cost(label, value, total=False):
        w = "700" if total else "400"
        b = "" if total else f"border-bottom:1px solid #F3F4F6;"
        return (f'<tr><td style="padding:6px 0;color:{TEXT};font-weight:600;{b}">{label}</td>'
                f'<td style="padding:6px 0;color:{BRAND_DARK};text-align:right;font-weight:{w};{b}">{value}</td></tr>')

    body = f"""
      <h2 style="margin:0 0 6px;font-size:18px;font-weight:700;color:{BRAND_DARK};text-align:center;">
        Thanks for choosing <a href="{settings.APP_URL}" {link}>TempCover</a>
      </h2>
      <p style="margin:0 0 24px;font-size:16px;font-weight:700;color:{BRAND_DARK};text-align:center;">
        Your temporary insurance is all ready to go!
      </p>

      <p style="margin:0 0 12px;font-size:14px;color:{TEXT};">Hi {driver_name},</p>
      <p style="margin:0 0 12px;font-size:14px;color:{TEXT};line-height:1.6;">
        There's nothing more you need to do — everything is taken care of. Your insurance policy
        will start at your chosen time.
      </p>
      <p style="margin:0 0 12px;font-size:14px;color:{TEXT};line-height:1.6;">
        A summary of your policy is provided below, along with a link where you can view and
        print your documents.
      </p>
      <p style="margin:0 0 24px;font-size:13px;color:{MUTED};font-style:italic;line-height:1.6;">
        This policy is intended for customers who need short-term vehicle insurance.
        You can read our Customer Terms of Business <a href="{settings.APP_URL}/terms" {link}>here</a>.
      </p>

      <div style="text-align:center;margin:28px 0;">
        <a href="{verify_url}" style="display:inline-block;padding:14px 36px;background:{BRAND};color:#ffffff;text-decoration:none;border-radius:8px;font-size:15px;font-weight:700;letter-spacing:0.3px;">
          View your policy documents
        </a>
      </div>

      <hr style="border:none;border-top:1px solid {BORDER};margin:28px 0;">

      <h3 style="margin:0 0 16px;font-size:15px;font-weight:700;color:{BRAND_DARK};">Policy summary</h3>
      <table style="width:100%;border-collapse:collapse;font-size:14px;">
        {row("Policy number:", policy_number, strong=True)}
        {row("Policy holder:", driver_name)}
        {row("Vehicle:", vehicle_make_model, accent=True)}
        {row("Vehicle registration:", vehicle_reg, accent=True)}
        {row("Duration:", duration)}
        {row("Start date/time:", _short(start_datetime))}
        {row("End date/time:", _short(end_datetime))}
      </table>

      <p style="margin:20px 0 12px;font-size:14px;color:{TEXT};line-height:1.6;">
        You have been charged <strong style="color:{BRAND};">£{bd['total']}</strong> and a breakdown of the cost is below:
      </p>
      <table style="width:100%;border-collapse:collapse;font-size:14px;">
        {cost("Insurer premium:", f"£{bd['insurer_premium']}")}
        {cost("Insurance premium tax:", f"£{bd['ipt']}")}
        {cost("TempCover fee:", f"£{bd['admin_fee']}")}
        {cost("Campaign discount:", f"-£{bd['discount']}")}
        {cost("Total charged:", f"£{bd['total']}", total=True)}
      </table>

      <hr style="border:none;border-top:1px solid {BORDER};margin:28px 0;">

      <p style="margin:0 0 12px;font-size:13px;color:{TEXT};line-height:1.6;">
        Your insurance information will be transmitted to the
        <a href="https://enquiry.navigate.mib.org.uk/checkyourvehicle" {link}>Motor Insurance Database (MID)</a>
        within the required timeframe. Due to the temporary nature of your policy,
        there is a possibility that it may expire before the database is updated.
      </p>
      <p style="margin:0 0 12px;font-size:13px;color:{TEXT};line-height:1.6;">
        We recommend printing your insurance certificate and keeping it with you when driving,
        as it provides valid proof of insurance and your legal entitlement to operate the vehicle.
      </p>
      <p style="margin:0 0 24px;font-size:13px;color:{TEXT};line-height:1.6;">
        We look forward to serving you again in the future.
      </p>

      <hr style="border:none;border-top:1px solid {BORDER};margin:24px 0;">

      <p style="margin:0 0 10px;font-size:11px;color:{MUTED};line-height:1.7;">
        TempCover is an insurance intermediary authorised and regulated by the Financial Conduct Authority (FCA).
        You can check this on the Financial Services Register at
        <a href="https://www.fca.org.uk" {link}>www.fca.org.uk</a>.
      </p>
      <p style="margin:0 0 10px;font-size:11px;color:{MUTED};line-height:1.7;">
        <strong style="color:{TEXT};">Important confidentiality notice:</strong> this email and the information it contains
        may be confidential. If you have received this email in error, please notify us immediately and delete it from your system.
      </p>
      <p style="margin:0 0 10px;font-size:11px;color:{MUTED};line-height:1.7;">
        You are receiving this email as part of our policy confirmation service. This does not relate to
        any marketing communication preferences you may have set.
      </p>
      <p style="margin:0 0 10px;font-size:11px;color:{MUTED};line-height:1.7;">
        TEMPCOVER LTD — REGISTERED IN ENGLAND AND WALES.<br>
        Registered office: United Kingdom.
      </p>
      <p style="margin:0;font-size:11px;color:#9CA3AF;line-height:1.7;">
        <a href="{settings.APP_URL}/terms" {link}>Terms</a> &nbsp;|&nbsp;
        <a href="{settings.APP_URL}/privacy" {link}>Privacy Policy</a> &nbsp;|&nbsp;
        <a href="{settings.APP_URL}/contact" {link}>Contact Us</a>
      </p>
    """
    return _shell("TempCover Insurance - Policy Confirmation", body)


def _build_cancellation_email_html(driver_name: str, policy_number: str) -> str:
    link = f'style="color:{BRAND};text-decoration:none;font-weight:600;"'
    body = f"""
      <h2 style="margin:0 0 18px;font-size:18px;font-weight:700;color:{BRAND_DARK};text-align:center;">
        Your policy has been cancelled
      </h2>
      <p style="margin:0 0 12px;font-size:14px;color:{TEXT};">Hi {driver_name},</p>
      <p style="margin:0 0 12px;font-size:14px;color:{TEXT};line-height:1.6;">
        We're writing to confirm that your TempCover policy
        <strong style="color:{BRAND_DARK};">{policy_number}</strong>
        has been cancelled and is no longer in force.
      </p>
      <p style="margin:0 0 12px;font-size:14px;color:{TEXT};line-height:1.6;">
        If this cancellation was unexpected or you have any questions, please contact us at
        <a href="mailto:{settings.SUPPORT_EMAIL}" {link}>{settings.SUPPORT_EMAIL}</a>
        and we'll get back to you within 24 hours.
      </p>
      <hr style="border:none;border-top:1px solid {BORDER};margin:24px 0;">
      <p style="margin:0 0 10px;font-size:11px;color:{MUTED};line-height:1.7;">
        TempCover is an insurance intermediary authorised and regulated by the Financial Conduct Authority (FCA).
      </p>
    """
    return _shell("TempCover Insurance - Policy Cancelled", body)


def _send(to_email: str, to_name: str, subject: str, html: str) -> bool:
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
            return True
    except httpx.HTTPStatusError as e:
        print(f"[EMAIL ERROR] HTTP {e.response.status_code}: {e.response.text}")
        return False
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False


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
) -> bool:
    verify_url = f"{settings.APP_URL}/driver/login"

    if not settings.BREVO_API_KEY:
        print(f"\n{'='*50}")
        print(f"[DEV EMAIL] To:         {to_email}")
        print(f"[DEV EMAIL] Policy:     {policy_number}")
        print(f"[DEV EMAIL] Verify URL: {verify_url}")
        print(f"{'='*50}\n")
        return True

    html = _build_email_html(
        driver_name=driver_name,
        policy_number=policy_number,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        vehicle_reg=vehicle_reg,
        vehicle_make_model=vehicle_make_model,
        price=price,
        verify_url=verify_url,
    )
    return _send(to_email, driver_name, f"TempCover Insurance — Policy confirmation {policy_number}", html)


def send_policy_cancellation_email(to_email: str, driver_name: str, policy_number: str) -> bool:
    if not settings.BREVO_API_KEY:
        print(f"\n{'='*50}")
        print(f"[DEV EMAIL] Cancellation")
        print(f"[DEV EMAIL] To:     {to_email}")
        print(f"[DEV EMAIL] Policy: {policy_number}")
        print(f"{'='*50}\n")
        return True

    html = _build_cancellation_email_html(driver_name=driver_name, policy_number=policy_number)
    return _send(to_email, driver_name, f"TempCover Insurance — Policy {policy_number} cancelled", html)
