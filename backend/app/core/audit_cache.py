"""Short-lived in-memory cache for audit results.

Keeps each audit result briefly (keyed by URL) so the PDF can reuse the exact
result the screen showed, instead of running a second audit that would give
slightly different numbers.
"""
import time

TTL_SECONDS = 600      # نحفظ النتيجة ١٠ دقائق
MAX_ENTRIES = 256      # أقصى عدد نتائج محفوظة

# كل نتيجة تنحفظ هنا: { "الرابط": (وقت_الحفظ, النتيجة) }
_store: dict[str, tuple[float, dict]] = {}


def set_result(url: str, result: dict) -> None:
    """نحفظ نتيجة تحليل رابط معيّن."""
    if url not in _store and len(_store) >= MAX_ENTRIES:
        oldest = min(_store, key=lambda u: _store[u][0])   # امسحي الأقدم لو امتلأ
        del _store[oldest]
    _store[url] = (time.time(), result)


def get_result(url: str) -> dict | None:
    """نرجّع النتيجة المحفوظة لو موجودة ولسا جديدة، وإلا None."""
    entry = _store.get(url)
    if entry is None:
        return None
    saved_at, result = entry
    if time.time() - saved_at > TTL_SECONDS:   # انتهت مهلتها
        del _store[url]
        return None
    return result