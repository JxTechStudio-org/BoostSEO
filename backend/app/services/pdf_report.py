from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


def _draw_watermark(c, width, height):
    c.saveState()
    c.setFont("Helvetica-Bold", 72)
    c.setFillColorRGB(0.92, 0.92, 0.92)
    c.translate(width / 2, height / 2)
    c.rotate(40)
    c.drawCentredString(0, 0, "BoostSEO")
    c.restoreState()


def build_pdf(data: dict, file_path: str) -> None:
    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter
    score = data["score"]
    meta = data["meta"]

    _draw_watermark(c, width, height)

    # ── Header ──────────────────────────────────────────────────────────────
    c.setFont("Helvetica-Bold", 22)
    c.setFillColorRGB(0.1, 0.4, 0.7)
    c.drawString(50, height - 55, "BoostSEO — Technical SEO Report")

    c.setFont("Helvetica", 9)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawString(50, height - 72, f"URL: {data['url']}")
    c.drawString(50, height - 84, data["summary"])

    # score circle
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

    # stats row
    c.setFont("Helvetica", 9)
    c.setFillColorRGB(0, 0.55, 0.2)
    c.drawString(50, height - 100, f"Passed: {meta['checks_passed']}")
    c.setFillColorRGB(0.65, 0.45, 0)
    c.drawString(130, height - 100, f"Warnings: {meta['checks_warned']}")
    c.setFillColorRGB(0.75, 0.1, 0.1)
    c.drawString(230, height - 100, f"Failed: {meta['checks_failed']}")
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawString(310, height - 100, f"Response: {meta['response_time_ms']}ms")

    # divider
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.line(50, height - 110, width - 50, height - 110)

    y = height - 128

    def check_page_break():
        nonlocal y
        if y < 60:
            c.showPage()
            _draw_watermark(c, width, height)
            y = height - 50

    # ── Category sections ────────────────────────────────────────────────────
    for cat in data["categories"]:
        check_page_break()

        c.setFont("Helvetica-Bold", 11)
        c.setFillColorRGB(0.1, 0.4, 0.7)
        c.drawString(50, y, f"{cat['name']}  —  {cat['score']}%")
        c.setStrokeColorRGB(0.7, 0.7, 0.7)
        c.line(50, y - 4, width - 50, y - 4)
        y -= 18

        c.setFont("Helvetica-Bold", 8)
        c.setFillColorRGB(0.3, 0.3, 0.3)
        c.drawString(50, y, "Check")
        c.drawString(185, y, "Status")
        c.drawString(255, y, "Message")
        y -= 14

        for check in cat["checks"]:
            check_page_break()
            c.setFont("Helvetica-Bold", 8)
            c.setFillColorRGB(0, 0, 0)
            c.drawString(50, y, check["name"][:24])

            status = check["status"]
            if status == "Passed":
                c.setFillColorRGB(0, 0.55, 0.2)
            elif status == "Warning":
                c.setFillColorRGB(0.65, 0.45, 0)
            else:
                c.setFillColorRGB(0.75, 0.1, 0.1)
            c.drawString(185, y, status)

            c.setFillColorRGB(0.2, 0.2, 0.2)
            c.setFont("Helvetica", 8)
            c.drawString(255, y, check["message"][:60])
            y -= 14

        y -= 8

    c.save()
