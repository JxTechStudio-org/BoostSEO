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

# CORS: only these origins may read the API with credentials. Wide-open
# allow_origins=["*"] with allow_credentials is unsafe (any site could read the
# API as the signed-in user). Override via the CORS_ALLOWED_ORIGINS env var
# (comma-separated). Front-end and API share one origin in production.
_DEFAULT_ORIGINS = "https://boostseo.jxtechstudio.com,http://localhost:3012"
ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv("CORS_ALLOWED_ORIGINS", _DEFAULT_ORIGINS).split(",")
    if o.strip()
]
