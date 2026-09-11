"""
Shared utilities, constants, and design tokens for PDF generation.
"""

import concurrent.futures
from datetime import datetime


# ---------------------------------------------------------------------------
# Subprocess-isolated WeasyPrint — prevents a segfault from killing Uvicorn
# ---------------------------------------------------------------------------

def _weasyprint_render(html: str) -> bytes:
    """Runs inside a fresh subprocess — isolated from the main process."""
    from weasyprint import HTML
    return HTML(string=html).write_pdf()


def safe_weasyprint(html: str, timeout: int = 25) -> "bytes | None":
    """
    Renders HTML to PDF via WeasyPrint in a subprocess with a timeout.
    Returns bytes on success, None if WeasyPrint crashes, raises, or times out.
    The main Uvicorn worker is never touched even on a C-level segfault.
    """
    try:
        with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_weasyprint_render, html)
            return future.result(timeout=timeout)
    except concurrent.futures.TimeoutError:
        print("[PDF] WeasyPrint timed out — using ReportLab fallback")
        return None
    except Exception as e:
        print(f"[PDF] WeasyPrint failed ({e}) — using ReportLab fallback")
        return None
from reportlab.lib import colors
from reportlab.lib.units import mm


# ---------------------------------------------------------------------------
# Design tokens — change once, applied everywhere
# ---------------------------------------------------------------------------

class Theme:
    # Brand colours
    BRAND_BLUE   = colors.HexColor("#003087")
    BRAND_DARK   = colors.HexColor("#1a1a2e")
    ACCENT       = colors.HexColor("#e8f0fe")
    HEADER_BG    = colors.HexColor("#003087")
    HEADER_TEXT  = colors.white
    ROW_ALT      = colors.HexColor("#f4f7fb")
    BORDER       = colors.HexColor("#c5cfe0")
    TEXT_PRIMARY = colors.HexColor("#0d1b2a")
    TEXT_MUTED   = colors.HexColor("#5a6a7a")

    # Fonts
    FONT_BOLD    = "Helvetica-Bold"
    FONT_REGULAR = "Helvetica"
    FONT_ITALIC  = "Helvetica-Oblique"

    # Sizes
    FONT_TITLE   = 16
    FONT_HEADING = 11
    FONT_BODY    = 10
    FONT_SMALL   = 8
    FONT_TINY    = 7


class Layout:
    LEFT_MARGIN  = 22 * mm
    RIGHT_MARGIN = 22 * mm
    LINE_HEIGHT  = 5 * mm
    FIELD_GAP    = 10 * mm


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------

def _to_dt(value: str | datetime) -> datetime:
    """Coerce an ISO-string or datetime → datetime."""
    if isinstance(value, str):
        return datetime.fromisoformat(value)
    return value


def fmt_time_date(dt: str | datetime) -> str:
    """13:44  26-03-2026"""
    return _to_dt(dt).strftime("%H:%M  %d-%m-%Y")


def fmt_time_date_long(dt: str | datetime) -> str:
    """13:44  26 March 2026"""
    return _to_dt(dt).strftime("%H:%M  %d %B %Y")


def fmt_date_short(dt: str | datetime) -> str:
    """26/03/2026"""
    return _to_dt(dt).strftime("%d/%m/%Y")


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def draw_wrapped_text(
    canvas,
    text: str,
    font_name: str,
    font_size: float,
    x: float,
    y: float,
    max_width: float,
    line_height: float = 5 * mm,
) -> float:
    """
    Word-wrap *text* within *max_width* and draw it starting at (x, y).
    Returns the y position after the last drawn line.
    Always measures real glyph widths — never uses char-index hacks.
    """
    canvas.setFont(font_name, font_size)
    words = text.split()
    line = ""

    for word in words:
        candidate = f"{line} {word}".lstrip()
        if canvas.stringWidth(candidate, font_name, font_size) <= max_width:
            line = candidate
        else:
            if line:
                canvas.drawString(x, y, line)
                y -= line_height
            line = word

    if line:
        canvas.drawString(x, y, line)
        y -= line_height

    return y


def draw_section_header(canvas, text: str, x: float, y: float, width: float) -> float:
    """
    Draw a filled blue band with white bold label.
    Returns y below the band.
    """
    band_h = 7 * mm
    canvas.setFillColor(Theme.HEADER_BG)
    canvas.rect(x, y - band_h + 2 * mm, width, band_h, fill=1, stroke=0)
    canvas.setFillColor(Theme.HEADER_TEXT)
    canvas.setFont(Theme.FONT_BOLD, Theme.FONT_SMALL + 1)
    canvas.drawString(x + 3 * mm, y - 3 * mm, text)
    canvas.setFillColor(Theme.TEXT_PRIMARY)
    return y - band_h - 1 * mm


def draw_key_value(
    canvas,
    label: str,
    value: str,
    x_label: float,
    x_value: float,
    y: float,
    font_size: float = 10,
) -> None:
    """Draw a bold label + regular value on one line."""
    canvas.setFont(Theme.FONT_BOLD, font_size)
    canvas.setFillColor(Theme.TEXT_PRIMARY)
    canvas.drawString(x_label, y, label)
    canvas.setFont(Theme.FONT_REGULAR, font_size)
    canvas.drawString(x_value, y, value)