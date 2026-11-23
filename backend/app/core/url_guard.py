"""SSRF protection for outbound requests.

Every URL the server fetches on a user's behalf is validated here before the
request is made, and again on every redirect hop. A URL is allowed only when
its scheme is http/https and none of the IP addresses its host resolves to are
private, loopback, link-local, reserved, multicast or unspecified. This blocks
requests to internal services (localhost, 10.x, 192.168.x, 169.254.x, ...).

The host is resolved once, here, and the request is then pinned to one of the
validated IP addresses. Without pinning, the HTTP client would resolve the name
a second time when it connects, so a host could return a public IP during
validation and an internal one a moment later (DNS rebinding) and slip past the
check. The original hostname is kept in the Host header and in the TLS SNI, so
HTTPS certificate verification still works against the real name.
"""
import asyncio
import ipaddress
from urllib.parse import urljoin, urlparse, urlunparse

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


async def _validated_ips(url: str) -> tuple[str, set[str]]:
    """Return the hostname and its validated public IPs, or raise UnsafeURLError."""
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
    return host, ips


async def validate_public_url(url: str) -> None:
    """Raise UnsafeURLError unless ``url`` is an http(s) URL to a public host."""
    await _validated_ips(url)


def _host_header(parsed) -> str:
    """The Host header value for the original URL (name, not the pinned IP)."""
    host = parsed.hostname or ""
    if ":" in host:                         # IPv6 literal needs brackets
        host = f"[{host}]"
    return f"{host}:{parsed.port}" if parsed.port else host


def _pin_to_ip(url: str, ip: str) -> str:
    """Return ``url`` with its host replaced by ``ip`` (IPv6 bracketed)."""
    parsed = urlparse(url)
    hostpart = f"[{ip}]" if ":" in ip else ip
    netloc = f"{hostpart}:{parsed.port}" if parsed.port else hostpart
    return urlunparse(parsed._replace(netloc=netloc))


async def safe_request(client, method: str, url: str, **kwargs):
    """Make a request, validating and pinning the URL and every redirect hop.

    For each hop the host is resolved once and checked; the request then goes to
    the validated IP (pinned), with the original hostname kept in the Host header
    and the TLS SNI. Redirects are followed manually so each new URL is validated
    and pinned the same way (a public URL cannot bounce to an internal one).
    """
    kwargs.pop("follow_redirects", None)
    headers = dict(kwargs.pop("headers", None) or {})
    current = url
    for _ in range(MAX_REDIRECTS + 1):
        host, ips = await _validated_ips(current)
        parsed = urlparse(current)
        hop_headers = {**headers, "Host": _host_header(parsed)}
        extensions = {"sni_hostname": host} if parsed.scheme == "https" else None
        resp = await client.request(
            method,
            _pin_to_ip(current, sorted(ips)[0]),
            headers=hop_headers,
            follow_redirects=False,
            extensions=extensions,
            **kwargs,
        )
        if resp.is_redirect and "location" in resp.headers:
            current = urljoin(current, resp.headers["location"])
            continue
        return resp
    raise UnsafeURLError("Too many redirects")


async def safe_get(client, url: str, **kwargs):
    return await safe_request(client, "GET", url, **kwargs)
