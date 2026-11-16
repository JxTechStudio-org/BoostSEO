"""SEO analysis endpoints: live audit and downloadable PDF report."""
from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.services.fetcher import fetch_and_audit
from app.services.pdf_report import build_pdf

router = APIRouter()


@router.get("/analyze")
async def analyze_endpoint(url: str) -> dict:
    """Fetch ``url`` and return the full SEO audit as JSON."""
    return await fetch_and_audit(url)


@router.get("/download-pdf")
async def download_pdf(url: str) -> FileResponse:
    """Fetch ``url``, build a PDF report, and return it as a download."""
    data = await fetch_and_audit(url)
    file_path = "SEO_Detailed_Report.pdf"
    build_pdf(data, file_path)
    return FileResponse(file_path, filename="SEO_Report.pdf")
