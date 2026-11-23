"""Shared constants for the BoostSEO backend."""
import os

# Browser-like User-Agent used for all outbound HTTP requests, so target sites
# serve the same markup a real browser would receive. Defined once here and
# imported wherever an httpx client is created.
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# CORS is not needed in production: the front-end and the API share one origin
# (the SPA calls the API at /api on the same domain, proxied by nginx), so the
# browser never makes a cross-origin request. The middleware is kept only for
# local cross-origin development and is driven entirely by the
# CORS_ALLOWED_ORIGINS env var (comma-separated). With the variable unset the
# list is empty, so no cross-origin is allowed and no insecure default (such as
# localhost) ever ships to production. Wide-open allow_origins=["*"] with
# credentials would let any site read the API as the signed-in user.
def parse_origins(raw: str) -> list[str]:
    return [o.strip() for o in raw.split(",") if o.strip()]


ALLOWED_ORIGINS = parse_origins(os.getenv("CORS_ALLOWED_ORIGINS", ""))
