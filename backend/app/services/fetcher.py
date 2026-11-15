"""Fetch a page and run the SEO audit on its HTML."""
import time

import httpx
from fastapi import HTTPException

from app.core.constants import BROWSER_HEADERS
from app.services.seo_engine import run_audit


async def fetch_and_audit(url: str) -> dict:
    """Fetch the page at ``url`` and return its SEO audit."""
    if not url.startswith("http"):
        url = "https://" + url
    async with httpx.AsyncClient(follow_redirects=True, timeout=20.0, headers=BROWSER_HEADERS) as client:
        t0 = time.time()
        try:
            response = await client.get(url)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Connection failed: {e}")
        response_time_ms = (time.time() - t0) * 1000
    return await run_audit(response.text, str(response.url), response_time_ms)
