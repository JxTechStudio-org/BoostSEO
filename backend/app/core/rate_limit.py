"""A small in-memory per-client rate limiter for expensive endpoints.

Keeps, per client key (usually an IP), the timestamps of recent calls and rejects
a call once more than ``max_calls`` happened within the last ``window_seconds``.
This mirrors the approach already used by the comments endpoint, packaged so the
analysis and PDF endpoints can reuse it.
"""
import time

from fastapi import HTTPException, Request


def client_ip(request: Request) -> str:
    """The caller's IP, trusting nginx's X-Real-IP (it overwrites any spoofed
    value), then the last X-Forwarded-For hop, then the socket peer."""
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[-1].strip()
    return request.client.host if request.client else "unknown"


class RateLimiter:
    def __init__(self, max_calls: int, window_seconds: float):
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self._hits: dict[str, list[float]] = {}

    def check(self, key: str) -> None:
        """Record one call for ``key`` or raise 429 if it is over the limit."""
        now = time.time()
        # Drop keys whose calls have all aged out, so the map can't grow forever.
        for k in [k for k, ts in self._hits.items()
                  if all(now - t >= self.window_seconds for t in ts)]:
            del self._hits[k]

        recent = [t for t in self._hits.get(key, []) if now - t < self.window_seconds]
        if len(recent) >= self.max_calls:
            raise HTTPException(
                status_code=429, detail="Too many requests. Please slow down."
            )
        recent.append(now)
        self._hits[key] = recent
