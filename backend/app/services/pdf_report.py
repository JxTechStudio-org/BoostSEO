from datetime import date

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase.pdfmetrics import stringWidth

# Column layout for the checks table
NAME_X = 50
STATUS_X = 185
MSG_X = 255
NAME_WIDTH = STATUS_X - NAME_X - 10      # wrap width for the check name
LINE_H = 11                              # height of one wrapped line

# The same guides shown on the site (frontend/src/resources). Mirror the titles
# and links here so the report points readers to the existing educational
# content instead of duplicating it. Update SITE_URL if the domain changes.
SITE_URL = "https://boostseo.jxtechstudio.com"
SEO_GUIDES = [
    {
        "title": "The Complete Technical SEO Checklist",
        "desc": "The 21 technical checks that most commonly break a site's search visibility, and how to fix each one.",
        "url": f"{SITE_URL}/resources/technical-seo-checklist",
    },
    {
        "title": "Meta Tags Guide: Title, Description & Open Graph",
        "desc": "What each meta tag does, the length limits that matter, and good vs. bad examples.",
        "url": f"{SITE_URL}/resources/meta-tags-guide",
    },
    {
        "title": "How to Improve Page Speed (Without a Rebuild)",
        "desc": "The highest-impact, lowest-effort fixes for slow pages, in the order to do them.",
        "url": f"{SITE_URL}/resources/page-speed-guide",
    },
]


def _draw_watermark(c, width, height):
    c.saveState()
    c.setFont("Helvetica-Bold", 72)
    c.setFillColorRGB(0.92, 0.92, 0.92)
    c.translate(width / 2, height / 2)
    c.rotate(40)
    c.drawCentredString(0, 0, "BoostSEO")
    c.restoreState()


def _wrap_text(text: str, font: str, size: int, max_width: float) -> list[str]:
    """Wrap text to ``max_width``, breaking on spaces and, when a single token is
    still too wide (e.g. a long URL with no spaces), breaking it by character."""
    lines: list[str] = []
    for soft in simpleSplit(text, font, size, max_width):
        if stringWidth(soft, font, size) <= max_width:
            lines.append(soft)
            continue
        cur = ""
        for ch in soft:
            if stringWidth(cur + ch, font, size) <= max_width:
                cur += ch
            else:
                lines.append(cur)
                cur = ch
        if cur:
            lines.append(cur)
    return lines or [""]


def _wrap_check(check: dict, name_width: float, msg_width: float):
    """Split a check's name and message into lines that fit their columns."""
    name_lines = _wrap_text(check["name"], "Helvetica-Bold", 8, name_width)
    msg_lines = _wrap_text(check["message"], "Helvetica", 8, msg_width)
    return name_lines, msg_lines


def build_pdf(data: dict, file_path: str) -> None:
    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter
    score = data["score"]
    meta = data["meta"]
    msg_width = width - 50 - MSG_X       # wrap width for the message column

    _draw_watermark(c, width, height)

    # ── Header ──────────────────────────────────────────────────────────────
    c.setFont("Helvetica-Bold", 22)
    c.setFillColorRGB(0.1, 0.4, 0.7)
    c.drawString(50, height - 55, "BoostSEO — Technical SEO Report")

    # Score circle (fixed, top-right); the meta text on the left wraps clear of it.
    cx, cy, r = 510, height - 68, 38
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.circle(cx, cy, r, stroke=1, fill=0)
    c.setFont("Helvetica-Bold", 20)
    if score >= 70:
        c.setFillColorRGB(0, 0.6, 0.2)
    elif score >= 50:
        c.setFillColorRGB(0.7, 0.5, 0)
    else:
        c.setFillColorRGB(0.8, 0.1, 0.1)
    c.drawCentredString(cx, cy - 7, str(score))

    # Meta text, wrapped so a long URL or summary can't overflow the page.
    meta_width = cx - r - 50 - 10        # stay left of the score circle
    ty = height - 72
    c.setFont("Helvetica", 9)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    for line in _wrap_text(f"URL: {data['url']}", "Helvetica", 9, meta_width):
        c.drawString(50, ty, line)
        ty -= 12
    c.drawString(50, ty, f"Generated: {date.today().isoformat()}")
    ty -= 12
    for line in _wrap_text(data["summary"], "Helvetica", 9, meta_width):
        c.drawString(50, ty, line)
        ty -= 12

    # Keep the rows below the score circle even when the meta text is short.
    ty = min(ty, cy - r - 8)

    # stats row
    c.setFont("Helvetica", 9)
    c.setFillColorRGB(0, 0.55, 0.2)
    c.drawString(50, ty, f"Passed: {meta['checks_passed']}")
    c.setFillColorRGB(0.65, 0.45, 0)
    c.drawString(130, ty, f"Warnings: {meta['checks_warned']}")
    c.setFillColorRGB(0.75, 0.1, 0.1)
    c.drawString(230, ty, f"Failed: {meta['checks_failed']}")
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawString(310, ty, f"Response: {meta['response_time_ms']}ms")
    ty -= 14

    # what the score means
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawString(50, ty,
                 "Score: 70+ good  ·  50-69 needs improvement  ·  below 50 poor")
    ty -= 8

    # divider
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.line(50, ty, width - 50, ty)

    y = ty - 18

    def new_page_if_needed(needed: float):
        nonlocal y
        if y - needed < 50:
            c.showPage()
            _draw_watermark(c, width, height)
            y = height - 50

    # ── Category sections ────────────────────────────────────────────────────
    for cat in data["categories"]:
        new_page_if_needed(32)

        c.setFont("Helvetica-Bold", 11)
        c.setFillColorRGB(0.1, 0.4, 0.7)
        c.drawString(50, y, f"{cat['name']}  —  {cat['score']}%")
        c.setStrokeColorRGB(0.7, 0.7, 0.7)
        c.line(50, y - 4, width - 50, y - 4)
        y -= 18

        c.setFont("Helvetica-Bold", 8)
        c.setFillColorRGB(0.3, 0.3, 0.3)
        c.drawString(NAME_X, y, "Check")
        c.drawString(STATUS_X, y, "Status")
        c.drawString(MSG_X, y, "Message")
        y -= 14

        for check in cat["checks"]:
            # wrap long text instead of cutting it off
            name_lines, msg_lines = _wrap_check(check, NAME_WIDTH, msg_width)
            row_h = max(len(name_lines), len(msg_lines), 1) * LINE_H
            new_page_if_needed(row_h)

            c.setFont("Helvetica-Bold", 8)
            c.setFillColorRGB(0, 0, 0)
            for i, line in enumerate(name_lines):
                c.drawString(NAME_X, y - i * LINE_H, line)

            status = check["status"]
            if status == "Passed":
                c.setFillColorRGB(0, 0.55, 0.2)
            elif status == "Warning":
                c.setFillColorRGB(0.65, 0.45, 0)
            else:
                c.setFillColorRGB(0.75, 0.1, 0.1)
            c.drawString(STATUS_X, y, status)

            c.setFont("Helvetica", 8)
            c.setFillColorRGB(0.2, 0.2, 0.2)
            for i, line in enumerate(msg_lines):
                c.drawString(MSG_X, y - i * LINE_H, line)

            y -= row_h + 3

        y -= 8

    # ── SEO Guides: point readers to the site's existing guides ──────────────
    new_page_if_needed(30 + len(SEO_GUIDES) * 34)
    c.setFont("Helvetica-Bold", 11)
    c.setFillColorRGB(0.1, 0.4, 0.7)
    c.drawString(50, y, "SEO Guides — learn how to fix these")
    c.setStrokeColorRGB(0.7, 0.7, 0.7)
    c.line(50, y - 4, width - 50, y - 4)
    y -= 18

    for guide in SEO_GUIDES:
        new_page_if_needed(34)
        c.setFont("Helvetica-Bold", 9)
        c.setFillColorRGB(0, 0, 0)
        c.drawString(50, y, guide["title"])
        y -= 12

        c.setFont("Helvetica", 8)
        c.setFillColorRGB(0.3, 0.3, 0.3)
        for line in simpleSplit(guide["desc"], "Helvetica", 8, width - 100):
            c.drawString(50, y, line)
            y -= 10

        c.setFont("Helvetica-Oblique", 8)
        c.setFillColorRGB(0.1, 0.4, 0.7)
        c.drawString(50, y, guide["url"])
        y -= 18

    c.save()