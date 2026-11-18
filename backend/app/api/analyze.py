"""SEO analysis endpoints: live audit and downloadable PDF report."""
from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.core import audit_cache
from app.services.fetcher import fetch_and_audit
from app.services.pdf_report import build_pdf

router = APIRouter()


@router.get("/analyze")
async def analyze_endpoint(url: str) -> dict:
    """Fetch ``url``, cache the result, and return the full SEO audit as JSON."""
    result = await fetch_and_audit(url)
    audit_cache.set_result(url, result)
    return result


@router.get("/download-pdf")
async def download_pdf(url: str) -> FileResponse:
    """Build the PDF from the same result the screen showed.

    Reusing the cached audit keeps the PDF's numbers identical to the on-screen
    report. If the cache has expired, we re-run the audit as a fallback.
    """
    data = audit_cache.get_result(url)
    if data is None:
        data = await fetch_and_audit(url)
    file_path = "SEO_Detailed_Report.pdf"
    build_pdf(data, file_path)
    return FileResponse(file_path, filename="SEO_Report.pdf")