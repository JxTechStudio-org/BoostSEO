"""Engine-level SSRF tests (task 3, finding 1).

The main page fetch is already guarded; these tests cover the two crawlability
checks (robots.txt and sitemap.xml), which previously called the shared client
directly and would follow a redirect into an internal address. They must now
route through the SSRF guard and refuse such a redirect.
"""
import asyncio

import httpx
import pytest

from app.services.seo_engine import _check_robots_txt, _check_sitemap


def run(coro):
    return asyncio.new_event_loop().run_until_complete(coro)


def _redirect_to_internal(request):
    # The public host bounces every first-party path to the cloud metadata IP.
    if request.url.host == "8.8.8.8":
        return httpx.Response(302, headers={"location": "http://169.254.169.254/"})
    return httpx.Response(200, text="SECRET internal data")


@pytest.mark.parametrize("check", [_check_robots_txt, _check_sitemap])
def test_crawl_checks_block_redirect_to_internal(check):
    async def go():
        transport = httpx.MockTransport(_redirect_to_internal)
        # follow_redirects=True on purpose: the guard (not the client flag) must
        # be what stops the internal hop. With the old direct client.get this
        # would follow the 302, reach the internal 200, and report "Passed".
        async with httpx.AsyncClient(transport=transport, follow_redirects=True) as client:
            result = await check("http://8.8.8.8", client)
        # The internal 200 must never be reached or reported as "Passed".
        assert result.status == "Warning"

    run(go())
