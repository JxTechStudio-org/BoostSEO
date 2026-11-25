"""SEO analysis endpoints: live audit and downloadable PDF report."""
import os
import tempfile

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from app.core.rate_limit import RateLimiter, client_ip
from app.services.fetcher import fetch_and_audit
from app.services.pdf_report import build_pdf

router = APIRouter()

# Both endpoints fetch an external site, so they are expensive; cap each client
# to 10 requests per minute to keep one caller from overloading the backend.
_analyze_limiter = RateLimiter(max_calls=10, window_seconds=60)
_pdf_limiter = RateLimiter(max_calls=10, window_seconds=60)


@router.get("/analyze")
async def analyze_endpoint(url: str, request: Request) -> dict:
    """Fetch ``url`` and return the full SEO audit as JSON."""
    _analyze_limiter.check(client_ip(request))
    return await fetch_and_audit(url)


@router.get("/download-pdf")
async def download_pdf(url: str, request: Request) -> FileResponse:
    """Fetch ``url``, build a PDF report, and return it as a download.

    Each request writes to its own unique temp file, which is deleted after the
    response is sent. This avoids the shared fixed filename that could leak one
    user's report to another under concurrent requests.
    """
    _pdf_limiter.check(client_ip(request))
    data = await fetch_and_audit(url)
    fd, file_path = tempfile.mkstemp(prefix="seo_report_", suffix=".pdf")
    os.close(fd)
    build_pdf(data, file_path)
    return FileResponse(
        file_path,
        filename="SEO_Report.pdf",
        background=BackgroundTask(os.remove, file_path),
    )
