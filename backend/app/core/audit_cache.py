"""Short-lived in-memory cache for audit results.

Keeps each audit result briefly (keyed by URL) so the PDF can reuse the exact
result the screen showed, instead of running a second audit that would give
slightly different numbers.
"""
import time

TTL_SECONDS = 600      # keep each result for 10 minutes
MAX_ENTRIES = 256      # cap on the number of stored results

# url -> (saved_at, result). The key is stripped so /analyze and /download-pdf
# resolve to the same entry even if one is called with surrounding whitespace.
_store: dict[str, tuple[float, dict]] = {}


def set_result(url: str, result: dict) -> None:
    """Store the audit result for a URL, evicting the oldest entry when full."""
    key = url.strip()
    if key not in _store and len(_store) >= MAX_ENTRIES:
        oldest = min(_store, key=lambda u: _store[u][0])   # drop the oldest
        del _store[oldest]
    _store[key] = (time.time(), result)


def get_result(url: str) -> dict | None:
    """Return the stored result if present and still fresh, otherwise None."""
    key = url.strip()
    entry = _store.get(key)
    if entry is None:
        return None
    saved_at, result = entry
    if time.time() - saved_at > TTL_SECONDS:   # expired
        del _store[key]
        return None
    return result
