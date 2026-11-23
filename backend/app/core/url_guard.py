"""SSRF protection for outbound requests.

Every URL the server fetches on a user's behalf is validated here before the
request is made, and again on every redirect hop. A URL is allowed only when
its scheme is http/https and none of the IP addresses its host resolves to are
private, loopback, link-local, reserved, multicast or unspecified. This blocks
requests to internal services (localhost, 10.x, 192.168.x, 169.254.x, ...).
"""
import asyncio
import ipaddress
from urllib.parse import urljoin, urlparse

ALLOWED_SCHEMES = {"http", "https"}
MAX_REDIRECTS = 5


class UnsafeURLError(ValueError):
    """Raised when a URL points at a disallowed scheme or an internal address."""


def _ip_is_blocked(ip_str: str) -> bool:
    ip = ipaddress.ip_address(ip_str)
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    )


async def _resolve(host: str) -> set[str]:
    loop = asyncio.get_event_loop()
    infos = await loop.getaddrinfo(host, None)
    return {info[4][0] for info in infos}


async def validate_public_url(url: str) -> None:
    """Raise UnsafeURLError unless ``url`` is an http(s) URL to a public host."""
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise UnsafeURLError(f"Scheme not allowed: {parsed.scheme or 'none'}")
    host = parsed.hostname
    if not host:
        raise UnsafeURLError("URL has no host")
    try:
        ipaddress.ip_address(host)          # host is already an IP literal
        ips = {host}
    except ValueError:
        ips = await _resolve(host)          # host is a name: resolve it
    if not ips:
        raise UnsafeURLError("Could not resolve host")
    for ip in ips:
        if _ip_is_blocked(ip):
            raise UnsafeURLError(f"Blocked internal address: {ip}")


async def safe_request(client, method: str, url: str, **kwargs):
    """Make a request, validating the URL and every redirect hop against SSRF.

    Automatic redirect following is disabled; redirects are followed manually so
    each hop is validated (a public URL cannot bounce to an internal one).
    """
    kwargs.pop("follow_redirects", None)
    current = url
    for _ in range(MAX_REDIRECTS + 1):
        await validate_public_url(current)
        resp = await client.request(method, current, follow_redirects=False, **kwargs)
        if resp.is_redirect and "location" in resp.headers:
            current = urljoin(current, resp.headers["location"])
            continue
        return resp
    raise UnsafeURLError("Too many redirects")


async def safe_get(client, url: str, **kwargs):
    return await safe_request(client, "GET", url, **kwargs)
