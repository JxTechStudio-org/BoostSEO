"""SEO analysis endpoints: live audit and downloadable PDF report."""
import os
import tempfile

from fastapi import APIRouter
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from app.services.fetcher import fetch_and_audit
from app.services.pdf_report import build_pdf

router = APIRouter()


@router.get("/analyze")
async def analyze_endpoint(url: str) -> dict:
    """Fetch ``url`` and return the full SEO audit as JSON."""
    return await fetch_and_audit(url)


@router.get("/download-pdf")
async def download_pdf(url: str) -> FileResponse:
    """Fetch ``url``, build a PDF report, and return it as a download.

    Each request writes to its own unique temp file, which is deleted after the
    response is sent. This avoids the shared fixed filename that could leak one
    user's report to another under concurrent requests.
    """
    data = await fetch_and_audit(url)
    fd, file_path = tempfile.mkstemp(prefix="seo_report_", suffix=".pdf")
    os.close(fd)
    build_pdf(data, file_path)
    return FileResponse(
        file_path,
        filename="SEO_Report.pdf",
        background=BackgroundTask(os.remove, file_path),
    )
