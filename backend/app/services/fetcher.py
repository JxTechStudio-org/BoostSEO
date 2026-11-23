"""Fetch a page and run the SEO audit on its HTML."""
import time

import httpx
from fastapi import HTTPException

from app.core.constants import BROWSER_HEADERS
from app.core.url_guard import UnsafeURLError, safe_get
from app.services.seo_engine import run_audit


async def fetch_and_audit(url: str) -> dict:
    """Fetch the page at ``url`` and return its SEO audit.

    The URL is validated against SSRF before the request and on every redirect.
    """
    if not url.startswith("http"):
        url = "https://" + url
    async with httpx.AsyncClient(timeout=20.0, headers=BROWSER_HEADERS) as client:
        t0 = time.time()
        try:
            response = await safe_get(client, url)
        except UnsafeURLError as e:
            raise HTTPException(status_code=400, detail=f"URL not allowed: {e}")
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Connection failed: {e}")
        response_time_ms = (time.time() - t0) * 1000
    return await run_audit(response.text, str(response.url), response_time_ms)
