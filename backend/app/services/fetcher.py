"""Fetch a page and run the SEO audit on its HTML."""
import time
from urllib.parse import urljoin

import httpx
from fastapi import HTTPException

from app.core.constants import BROWSER_HEADERS
from app.core.url_guard import MAX_REDIRECTS, UnsafeURLError, validate_public_url
from app.services.seo_engine import run_audit

FETCH_TIMEOUT_SECONDS = 20.0
MAX_PAGE_BYTES = 5_000_000          # 5 MB — reject pages too large to analyze


class PageTooLargeError(Exception):
    """Raised when a fetched page exceeds MAX_PAGE_BYTES."""


async def _fetch_html(client: httpx.AsyncClient, url: str, max_bytes: int):
    """Fetch ``url`` as text, returning (final_url, html).

    The URL is checked against SSRF on every redirect hop, and the body is
    streamed and aborted as soon as it passes ``max_bytes`` — so an oversized
    page is rejected before it is fully loaded into memory, instead of being
    downloaded whole and crashing the server.
    """
    current = url
    for _ in range(MAX_REDIRECTS + 1):
        await validate_public_url(current)
        async with client.stream("GET", current, follow_redirects=False) as resp:
            if resp.is_redirect and resp.headers.get("location"):
                current = urljoin(current, resp.headers["location"])
                continue
            declared = resp.headers.get("content-length")
            if declared and declared.isdigit() and int(declared) > max_bytes:
                raise PageTooLargeError
            body = bytearray()
            async for chunk in resp.aiter_bytes():
                body.extend(chunk)
                if len(body) > max_bytes:
                    raise PageTooLargeError
            html = body.decode(resp.encoding or "utf-8", errors="replace")
            return str(resp.url), html
    raise UnsafeURLError("Too many redirects")


async def fetch_and_audit(url: str) -> dict:
    """Fetch the page at ``url`` and return its SEO audit.

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
            final_url, html = await _fetch_html(client, url, MAX_PAGE_BYTES)
        except UnsafeURLError as e:
            raise HTTPException(status_code=400, detail=f"URL not allowed: {e}")
        except PageTooLargeError:
            raise HTTPException(status_code=413, detail="The page is too large to analyze.")
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504, detail="The site took too long to respond."
            )
        except (httpx.RequestError, OSError):
            raise HTTPException(status_code=502, detail="Could not connect to the site.")
        response_time_ms = (time.time() - t0) * 1000

    return await run_audit(html, final_url, response_time_ms)
