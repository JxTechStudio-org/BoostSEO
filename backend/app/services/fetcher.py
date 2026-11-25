"""Fetch a page and run the SEO audit on its HTML."""
import time

import httpx
from fastapi import HTTPException

from app.core.constants import BROWSER_HEADERS
from app.core.url_guard import UnsafeURLError, safe_get
from app.services.seo_engine import run_audit

FETCH_TIMEOUT_SECONDS = 20.0
MAX_PAGE_BYTES = 5_000_000          # 5 MB — reject pages too large to analyze


def _too_large(response: httpx.Response) -> bool:
    """True if the page is bigger than we're willing to analyze."""
    declared = response.headers.get("content-length")
    if declared and declared.isdigit() and int(declared) > MAX_PAGE_BYTES:
        return True
    return len(response.content) > MAX_PAGE_BYTES


async def fetch_and_audit(url: str) -> dict:
    """Fetch the page at ``url`` and return its SEO audit.

    The URL is validated against SSRF before the request and on every redirect.
    Bad URLs, slow sites and oversized pages return a clear HTTP error instead of
    letting the request crash the server.
    """
    if not url.startswith("http"):
        url = "https://" + url
    async with httpx.AsyncClient(
        timeout=FETCH_TIMEOUT_SECONDS, headers=BROWSER_HEADERS
    ) as client:
        t0 = time.time()
        try:
            response = await safe_get(client, url)
        except UnsafeURLError as e:
            raise HTTPException(status_code=400, detail=f"URL not allowed: {e}")
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504, detail="The site took too long to respond."
            )
        except (httpx.RequestError, OSError):
            raise HTTPException(status_code=502, detail="Could not connect to the site.")
        response_time_ms = (time.time() - t0) * 1000

    if _too_large(response):
        raise HTTPException(status_code=413, detail="The page is too large to analyze.")

    return await run_audit(response.text, str(response.url), response_time_ms)
