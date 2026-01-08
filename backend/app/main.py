from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import httpx
from bs4 import BeautifulSoup
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import time
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def perform_analysis(url: str):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    if not url.startswith('http'):
        url = 'https://' + url

    async with httpx.AsyncClient(follow_redirects=True, timeout=20.0) as client:
        start_time = time.time()
        try:
            response = await client.get(url, headers=headers)
            load_time = round(time.time() - start_time, 2)
        except Exception as e:
            return {"error": f"Connection failed: {str(e)}"}

        soup = BeautifulSoup(response.text, "lxml")
        
        # استخراج البيانات
        title = soup.title.string.strip() if soup.title else None
        desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        description = desc_tag["content"].strip() if desc_tag else None
        h1_tags = soup.find_all("h1")
        images = soup.find_all("img")
        images_missing_alt = [img for img in images if not img.get('alt')]
        links_count = len(soup.find_all("a"))

        total_score = 0
        checks = [] # لتخزين النتائج التفصيلية للعرض

        # 1. فحص العنوان (Title Tag)
        title_status = "Failed"
        title_msg = "Title tag is missing."
        current_title = "None"
        if title:
            current_title = title
            if 10 <= len(title) <= 60:
                title_status = "Passed"
                title_msg = "Title is perfectly optimized."
                total_score += 20
            else:
                title_status = "Warning"
                title_msg = f"Title is {len(title)} chars. Ideally 10-60."
                total_score += 10
        checks.append({"name": "Title Tag", "status": title_status, "message": title_msg, "value": current_title})

        # 2. فحص الوصف (Meta Description)
        desc_status = "Passed" if description else "Failed"
        desc_msg = "Meta description is present." if description else "Meta description is missing."
        if description: total_score += 20
        checks.append({"name": "Meta Description", "status": desc_status, "message": desc_msg, "value": description or "None"})

        # 3. فحص الـ H1 (H1 Header)
        h1_count = len(h1_tags)
        if h1_count == 1:
            h1_status = "Passed"
            h1_msg = "Exactly one H1 tag found. Excellent!"
            total_score += 15
        elif h1_count == 0:
            h1_status = "Failed"
            h1_msg = "No H1 tag found. Your page needs a main heading."
            total_score += 0
        else:
            h1_status = "Warning"
            h1_msg = f"Multiple H1 tags ({h1_count}) found. Use only one."
            total_score += 5
        checks.append({"name": "H1 Header", "status": h1_status, "message": h1_msg, "value": f"{h1_count} found"})

        # 4. فحص الصور (Image Alt Text)
        missing_count = len(images_missing_alt)
        if images and missing_count == 0:
            img_status = "Passed"
            img_msg = "All images have descriptive alt text."
            total_score += 15
        elif not images:
            img_status = "Passed"
            img_msg = "No images found, nothing to optimize."
            total_score += 15
        else:
            img_status = "Warning"
            img_msg = f"{missing_count} images are missing alt text."
            total_score += 5
        checks.append({"name": "Image Alt Text", "status": img_status, "message": img_msg, "value": f"{missing_count} issues"})

        # 5. فحص السرعة (Load Speed)
        if load_time < 2.0:
            speed_status = "Passed"
            speed_msg = f"Page loaded fast in {load_time}s."
            total_score += 15
        else:
            speed_status = "Warning"
            speed_msg = f"Page is slow ({load_time}s). Target < 2s."
            total_score += 7
        checks.append({"name": "Load Speed", "status": speed_status, "message": speed_msg, "value": f"{load_time}s"})

        # 6. فحص الروابط (Links)
        link_status = "Passed" if links_count > 0 else "Failed"
        link_msg = f"Found {links_count} links." if links_count > 0 else "No links found."
        if links_count > 0: total_score += 15
        checks.append({"name": "Links", "status": link_status, "message": link_msg, "value": f"{links_count} links"})

        return {
            "url": url,
            "score": total_score,
            "checks": checks, # هذه القائمة سهلة جداً للعرض في الـ Frontend
            "summary": f"Your SEO Score is {total_score}/100"
        }

@app.get("/analyze")
async def analyze_endpoint(url: str):
    return await perform_analysis(url)

@app.get("/download-pdf")
async def download_pdf(url: str):
    data = await perform_analysis(url)
    if "error" in data: return data
    
    file_path = "SEO_Detailed_Report.pdf"
    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 22)
    c.setFillColorRGB(0.1, 0.4, 0.7)
    c.drawString(50, height - 60, "SEO Performance Report")
    
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawString(50, height - 80, f"URL: {url}")
    
    # Score Circle (Visual Representation)
    score = data['score']
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.circle(500, height - 70, 40, stroke=1, fill=0)
    c.setFont("Helvetica-Bold", 20)
    c.setFillColorRGB(0, 0.5, 0) if score > 70 else c.setFillColorRGB(0.8, 0, 0)
    c.drawCentredString(500, height - 75, str(score))

    # Table Header
    y = height - 140
    c.setFont("Helvetica-Bold", 12)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(50, y, "Test Item")
    c.drawString(180, y, "Status")
    c.drawString(280, y, "Observations & Recommendations")
    c.line(50, y - 5, 550, y - 5)

    # Table Body
    y -= 25
    for check in data['checks']:
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, check['name'])
        
        # Color coding status
        if check['status'] == "Passed": c.setFillColorRGB(0, 0.5, 0)
        elif check['status'] == "Warning": c.setFillColorRGB(0.6, 0.4, 0)
        else: c.setFillColorRGB(0.8, 0, 0)
        
        c.drawString(180, y, check['status'])
        
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica", 9)
        c.drawString(280, y, check['message'])
        y -= 25

    c.save()
    return FileResponse(file_path, filename="SEO_Report.pdf")