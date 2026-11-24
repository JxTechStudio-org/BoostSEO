"""SEO analysis endpoints: live audit and downloadable PDF report."""
import os
import tempfile
from datetime import date
from urllib.parse import urlparse

from fastapi import APIRouter
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from app.core import audit_cache
from app.services.fetcher import fetch_and_audit
from app.services.pdf_report import build_pdf

router = APIRouter()


def _report_filename(url: str) -> str:
    """Build the download filename from the site's domain and today's date."""
    host = urlparse(url if url.startswith("http") else f"https://{url}").hostname or "report"
    return f"SEO_Report_{host}_{date.today().isoformat()}.pdf"


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
    report; if the cache has expired we re-run the audit as a fallback. Each
    request writes to its own unique temp file, deleted after the response is
    sent, and the download is named after the site's domain and the report date.
    """
    data = audit_cache.get_result(url)
    if data is None:
        data = await fetch_and_audit(url)
    fd, file_path = tempfile.mkstemp(prefix="seo_report_", suffix=".pdf")
    os.close(fd)
    try:
        build_pdf(data, file_path)
    except Exception:
        # On success the temp file is removed by the background task below; if
        # building the PDF fails there is no response to attach that task to, so
        # remove the empty temp file here before re-raising.
        os.remove(file_path)
        raise
    return FileResponse(
        file_path,
        filename=_report_filename(url),
        background=BackgroundTask(os.remove, file_path),
    )