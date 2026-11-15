"""Shared constants for the BoostSEO backend."""

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
