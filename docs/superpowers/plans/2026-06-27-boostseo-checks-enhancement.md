# BoostSEO Checks Enhancement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand BoostSEO from 6 basic checks to 21 thorough checks, grouped by category in the UI with failed/warning checks surfaced first.

**Architecture:** All check logic moves into `seo_engine.py` which exposes a single `run_audit()` async function. `main.py` shrinks to HTTP fetch + engine call + return. The frontend adds a `CategoryCard` component and replaces the flat grid with grouped category sections.

**Tech Stack:** Python 3.11, FastAPI, BeautifulSoup4, HTTPX, asyncio, ReportLab — React 19, Vite, Tailwind CSS

## Global Constraints

- Python file: `SEO/backend/app/services/seo_engine.py`
- Python entry: `SEO/backend/app/main.py`
- Frontend components: `SEO/frontend/src/`
- All check statuses are exactly: `"Passed"` | `"Warning"` | `"Failed"`
- Category names are exactly: `"Meta & Social"` | `"Content"` | `"Technical"` | `"Performance"` | `"Crawlability"`
- Broken links capped at 20 unique hrefs; each deep check has a 5-second timeout
- PDF file written to `"SEO_Detailed_Report.pdf"` (existing filename, unchanged)
- Docker containers: backend `boostseo-backend`, frontend `boostseo-frontend`, compose file at `SEO/docker-compose.yml`

---

### Task 1: Rewrite seo_engine.py — data structures + all 21 check functions + run_audit

**Files:**
- Rewrite: `SEO/backend/app/services/seo_engine.py`
- Create: `SEO/backend/tests/__init__.py`
- Create: `SEO/backend/tests/test_seo_engine.py`

**Interfaces:**
- Produces: `run_audit(html: str, url: str, response_time_ms: float) -> dict` — the dict matches the API response shape defined in the spec

- [ ] **Step 1: Create tests directory and write failing tests**

```bash
mkdir -p /root/jana/projects/BoostSEO/SEO/backend/tests
touch /root/jana/projects/BoostSEO/SEO/backend/tests/__init__.py
```

Write `/root/jana/projects/BoostSEO/SEO/backend/tests/test_seo_engine.py`:

```python
import pytest
import asyncio
from app.services.seo_engine import run_audit

MINIMAL_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <title>Hello World Page</title>
  <meta name="description" content="A test page description.">
  <link rel="canonical" href="https://example.com/">
  <meta property="og:title" content="Hello OG">
  <meta property="og:description" content="OG desc">
  <meta property="og:image" content="https://example.com/img.jpg">
  <meta name="twitter:card" content="summary">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="icon" href="/favicon.ico">
  <script type="application/ld+json">{"@type": "WebPage"}</script>
</head>
<body>
  <h1>Main Heading</h1>
  <h2>Section One</h2>
  <p>This is a paragraph with enough words to pass the word count check.
     We need at least three hundred words here so let me write enough content
     to satisfy the requirement. Lorem ipsum dolor sit amet consectetur
     adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna
     aliqua ut enim ad minim veniam quis nostrud exercitation ullamco laboris
     nisi ut aliquip ex ea commodo consequat duis aute irure dolor in
     reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
     pariatur excepteur sint occaecat cupidatat non proident sunt in culpa qui
     officia deserunt mollit anim id est laborum sed ut perspiciatis unde omnis
     iste natus error sit voluptatem accusantium doloremque laudantium totam rem
     aperiam eaque ipsa quae ab illo inventore veritatis et quasi architecto
     beatae vitae dicta sunt explicabo nemo enim ipsam voluptatem quia voluptas
     sit aspernatur aut odit aut fugit sed quia consequuntur magni dolores eos
     qui ratione voluptatem sequi nesciunt neque porro quisquam est qui dolorem
     ipsum quia dolor sit amet consectetur adipisci velit.</p>
  <img src="img1.jpg" alt="A descriptive alt text">
  <a href="https://example.com/page1">Internal link</a>
  <a href="https://external.com">External link</a>
</body>
</html>"""

NO_TITLE_HTML = "<html><head></head><body><h1>Hi</h1><p>Content here.</p></body></html>"

NOINDEX_HTML = """<html lang="en"><head>
  <title>Blocked Page</title>
  <meta name="robots" content="noindex, nofollow">
</head><body><h1>Hi</h1></body></html>"""


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def test_run_audit_returns_required_keys():
    result = run(run_audit(MINIMAL_HTML, "https://example.com", 800.0))
    assert "url" in result
    assert "score" in result
    assert "summary" in result
    assert "checks" in result
    assert "categories" in result
    assert "meta" in result


def test_score_is_between_0_and_100():
    result = run(run_audit(MINIMAL_HTML, "https://example.com", 800.0))
    assert 0 <= result["score"] <= 100


def test_category_names_are_correct():
    result = run(run_audit(MINIMAL_HTML, "https://example.com", 800.0))
    names = [c["name"] for c in result["categories"]]
    assert "Meta & Social" in names
    assert "Content" in names
    assert "Technical" in names
    assert "Performance" in names
    assert "Crawlability" in names


def test_checks_within_categories_sorted_failed_first():
    # Use HTML that produces at least one failure
    result = run(run_audit(NO_TITLE_HTML, "https://example.com", 800.0))
    for cat in result["categories"]:
        statuses = [c["status"] for c in cat["checks"]]
        order = {"Failed": 0, "Warning": 1, "Passed": 2}
        assert statuses == sorted(statuses, key=lambda s: order[s])


def test_https_check_passes_for_https_url():
    result = run(run_audit(MINIMAL_HTML, "https://example.com", 800.0))
    tech_cat = next(c for c in result["categories"] if c["name"] == "Technical")
    https_check = next(c for c in tech_cat["checks"] if c["name"] == "HTTPS")
    assert https_check["status"] == "Passed"


def test_https_check_fails_for_http_url():
    result = run(run_audit(MINIMAL_HTML, "http://example.com", 800.0))
    tech_cat = next(c for c in result["categories"] if c["name"] == "Technical")
    https_check = next(c for c in tech_cat["checks"] if c["name"] == "HTTPS")
    assert https_check["status"] == "Failed"


def test_noindex_fails_robots_check():
    result = run(run_audit(NOINDEX_HTML, "https://example.com", 800.0))
    crawl_cat = next(c for c in result["categories"] if c["name"] == "Crawlability")
    robots_check = next(c for c in crawl_cat["checks"] if c["name"] == "Robots Meta Tag")
    assert robots_check["status"] == "Failed"


def test_slow_page_warns_or_fails():
    result = run(run_audit(MINIMAL_HTML, "https://example.com", 4500.0))
    perf_cat = next(c for c in result["categories"] if c["name"] == "Performance")
    speed_check = perf_cat["checks"][0]
    assert speed_check["status"] in ("Warning", "Failed")


def test_missing_title_fails():
    result = run(run_audit(NO_TITLE_HTML, "https://example.com", 800.0))
    meta_cat = next(c for c in result["categories"] if c["name"] == "Meta & Social")
    title_check = next(c for c in meta_cat["checks"] if c["name"] == "Title Tag")
    assert title_check["status"] == "Failed"


def test_meta_counts_correct():
    result = run(run_audit(MINIMAL_HTML, "https://example.com", 800.0))
    meta = result["meta"]
    total = meta["checks_passed"] + meta["checks_warned"] + meta["checks_failed"]
    assert total == meta["checks_total"]
```

- [ ] **Step 2: Run tests to verify they all fail (engine not implemented yet)**

```bash
cd /root/jana/projects/BoostSEO/SEO/backend
pip install pytest pytest-asyncio --quiet
python -m pytest tests/test_seo_engine.py -v 2>&1 | head -40
```

Expected: multiple errors — `ImportError` or `ModuleNotFoundError` since `run_audit` does not exist yet.

- [ ] **Step 3: Write the full seo_engine.py**

Write `/root/jana/projects/BoostSEO/SEO/backend/app/services/seo_engine.py`:

```python
from __future__ import annotations
import asyncio
from dataclasses import dataclass, asdict
from typing import List
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

CATEGORY_ORDER = [
    "Meta & Social",
    "Content",
    "Technical",
    "Performance",
    "Crawlability",
]

_STATUS_SORT = {"Failed": 0, "Warning": 1, "Passed": 2}

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


@dataclass
class CheckResult:
    name: str
    category: str
    status: str
    message: str
    value: str
    weight: int


@dataclass
class CategoryResult:
    name: str
    score: int
    checks: List[CheckResult]


@dataclass
class AuditMeta:
    checks_total: int
    checks_passed: int
    checks_warned: int
    checks_failed: int
    response_time_ms: int


# ── helpers ──────────────────────────────────────────────────────────────────

def _score(checks: List[CheckResult]) -> int:
    total_w = sum(c.weight for c in checks)
    if total_w == 0:
        return 0
    earned = sum(
        c.weight if c.status == "Passed" else (c.weight * 0.5 if c.status == "Warning" else 0)
        for c in checks
    )
    return round(earned / total_w * 100)


def _summary(score: int, checks: List[CheckResult]) -> str:
    failed = sum(1 for c in checks if c.status == "Failed")
    issues = sum(1 for c in checks if c.status in ("Failed", "Warning"))
    if score >= 90:
        return "Excellent SEO — your page is well optimized."
    if score >= 70:
        return f"Good SEO foundation. Fix {issues} issue(s) to improve further."
    if score >= 50:
        return f"Average SEO. {failed} critical issue(s) need attention."
    return f"Poor SEO. {failed} critical issue(s) are hurting your rankings."


# ── Meta & Social checks ─────────────────────────────────────────────────────

def _check_title(soup: BeautifulSoup) -> CheckResult:
    tag = soup.find("title")
    if not tag or not tag.text.strip():
        return CheckResult("Title Tag", "Meta & Social", "Failed",
                           "No title tag found.", "", 3)
    text = tag.text.strip()
    length = len(text)
    if length < 10:
        return CheckResult("Title Tag", "Meta & Social", "Warning",
                           f"Title is too short ({length} chars). Aim for 10–60.", text, 3)
    if length > 60:
        return CheckResult("Title Tag", "Meta & Social", "Warning",
                           f"Title is too long ({length} chars). Keep it under 60.", text[:60], 3)
    return CheckResult("Title Tag", "Meta & Social", "Passed",
                       f"Title is {length} characters — optimal.", text, 3)


def _check_meta_description(soup: BeautifulSoup) -> CheckResult:
    tag = soup.find("meta", attrs={"name": "description"})
    if not tag or not tag.get("content", "").strip():
        return CheckResult("Meta Description", "Meta & Social", "Failed",
                           "No meta description found.", "", 3)
    content = tag["content"].strip()
    display = content[:80] + "…" if len(content) > 80 else content
    return CheckResult("Meta Description", "Meta & Social", "Passed",
                       "Meta description is present.", display, 3)


def _check_canonical(soup: BeautifulSoup) -> CheckResult:
    tag = soup.find("link", attrs={"rel": "canonical"})
    if not tag or not tag.get("href", "").strip():
        return CheckResult("Canonical URL", "Meta & Social", "Warning",
                           "No canonical URL tag found. Add one to avoid duplicate content issues.", "", 2)
    return CheckResult("Canonical URL", "Meta & Social", "Passed",
                       "Canonical URL is set.", tag["href"], 2)


def _check_og_title(soup: BeautifulSoup) -> CheckResult:
    tag = soup.find("meta", property="og:title")
    if not tag or not tag.get("content", "").strip():
        return CheckResult("Open Graph Title", "Meta & Social", "Warning",
                           "og:title not found. Improves social media sharing.", "", 2)
    return CheckResult("Open Graph Title", "Meta & Social", "Passed",
                       "og:title is present.", tag["content"][:80], 2)


def _check_og_description(soup: BeautifulSoup) -> CheckResult:
    tag = soup.find("meta", property="og:description")
    if not tag or not tag.get("content", "").strip():
        return CheckResult("Open Graph Description", "Meta & Social", "Warning",
                           "og:description not found.", "", 1)
    return CheckResult("Open Graph Description", "Meta & Social", "Passed",
                       "og:description is present.", tag["content"][:80], 1)


def _check_og_image(soup: BeautifulSoup) -> CheckResult:
    tag = soup.find("meta", property="og:image")
    if not tag or not tag.get("content", "").strip():
        return CheckResult("Open Graph Image", "Meta & Social", "Warning",
                           "og:image not found. Social shares will have no preview image.", "", 1)
    return CheckResult("Open Graph Image", "Meta & Social", "Passed",
                       "og:image is present.", tag["content"], 1)


def _check_twitter_card(soup: BeautifulSoup) -> CheckResult:
    tag = soup.find("meta", attrs={"name": "twitter:card"})
    if not tag or not tag.get("content", "").strip():
        return CheckResult("Twitter Card", "Meta & Social", "Warning",
                           "twitter:card meta tag not found.", "", 1)
    return CheckResult("Twitter Card", "Meta & Social", "Passed",
                       "Twitter Card meta tag is present.", tag["content"], 1)


# ── Content checks ───────────────────────────────────────────────────────────

def _check_h1(soup: BeautifulSoup) -> CheckResult:
    h1s = soup.find_all("h1")
    count = len(h1s)
    if count == 0:
        return CheckResult("H1 Heading", "Content", "Failed",
                           "No H1 tag found. Every page needs a main heading.", "0 found", 3)
    if count > 1:
        return CheckResult("H1 Heading", "Content", "Warning",
                           f"{count} H1 tags found. Use exactly one per page.", f"{count} found", 3)
    return CheckResult("H1 Heading", "Content", "Passed",
                       "Exactly one H1 tag found.", h1s[0].get_text(strip=True)[:80], 3)


def _check_heading_hierarchy(soup: BeautifulSoup) -> CheckResult:
    h2s = soup.find_all("h2")
    h3s = soup.find_all("h3")
    if h2s:
        return CheckResult("Heading Hierarchy", "Content", "Passed",
                           f"{len(h2s)} H2 and {len(h3s)} H3 headings found.",
                           f"H2:{len(h2s)}, H3:{len(h3s)}", 2)
    if h3s:
        return CheckResult("Heading Hierarchy", "Content", "Warning",
                           "No H2 tags found but H3 tags exist. Add H2s for better structure.",
                           f"H2:0, H3:{len(h3s)}", 2)
    return CheckResult("Heading Hierarchy", "Content", "Failed",
                       "No subheadings (H2/H3) found. Add structure to improve readability.",
                       "H2:0, H3:0", 2)


def _check_word_count(soup: BeautifulSoup) -> CheckResult:
    text = soup.get_text(separator=" ")
    words = [w for w in text.split() if w.strip() and len(w) > 1]
    count = len(words)
    if count >= 300:
        return CheckResult("Word Count", "Content", "Passed",
                           f"Page has {count} words — good content depth.", f"{count} words", 2)
    if count >= 100:
        return CheckResult("Word Count", "Content", "Warning",
                           f"Page has only {count} words. Aim for 300+ for better rankings.", f"{count} words", 2)
    return CheckResult("Word Count", "Content", "Failed",
                       f"Page has only {count} words. Add more content.", f"{count} words", 2)


def _check_image_alt(soup: BeautifulSoup) -> CheckResult:
    images = soup.find_all("img")
    if not images:
        return CheckResult("Image Alt Text", "Content", "Passed",
                           "No images found on the page.", "0 images", 2)
    missing = [img for img in images if not img.get("alt", "").strip()]
    total = len(images)
    if not missing:
        return CheckResult("Image Alt Text", "Content", "Passed",
                           f"All {total} image(s) have alt text.", f"0/{total} missing", 2)
    if len(missing) == total:
        return CheckResult("Image Alt Text", "Content", "Failed",
                           f"All {total} image(s) are missing alt text.", f"{total}/{total} missing", 2)
    return CheckResult("Image Alt Text", "Content", "Warning",
                       f"{len(missing)} of {total} image(s) missing alt text.", f"{len(missing)}/{total} missing", 2)


# ── Technical checks ─────────────────────────────────────────────────────────

def _check_https(url: str) -> CheckResult:
    if url.startswith("https://"):
        return CheckResult("HTTPS", "Technical", "Passed",
                           "Site is served over HTTPS.", "https", 3)
    return CheckResult("HTTPS", "Technical", "Failed",
                       "Site is not using HTTPS. This is a Google ranking signal.", "http", 3)


def _check_viewport(soup: BeautifulSoup) -> CheckResult:
    tag = soup.find("meta", attrs={"name": "viewport"})
    if not tag:
        return CheckResult("Viewport Meta Tag", "Technical", "Failed",
                           "No viewport meta tag. Site may not be mobile-friendly.", "", 2)
    return CheckResult("Viewport Meta Tag", "Technical", "Passed",
                       "Viewport meta tag is present.", tag.get("content", ""), 2)


def _check_favicon(soup: BeautifulSoup) -> CheckResult:
    tag = soup.find("link", attrs={"rel": lambda r: r and "icon" in (r if isinstance(r, list) else [r])})
    if not tag:
        return CheckResult("Favicon", "Technical", "Warning",
                           "No favicon link tag found.", "", 1)
    return CheckResult("Favicon", "Technical", "Passed",
                       "Favicon is present.", tag.get("href", ""), 1)


def _check_language(soup: BeautifulSoup) -> CheckResult:
    html_tag = soup.find("html")
    lang = (html_tag.get("lang", "") or "").strip() if html_tag else ""
    if not lang:
        return CheckResult("Language Attribute", "Technical", "Warning",
                           "No lang attribute on <html>. Helps search engines identify the language.", "", 1)
    return CheckResult("Language Attribute", "Technical", "Passed",
                       f"Language is set to '{lang}'.", lang, 1)


def _check_structured_data(soup: BeautifulSoup) -> CheckResult:
    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    if not scripts:
        return CheckResult("Structured Data", "Technical", "Warning",
                           "No JSON-LD structured data found. Schema markup can enable rich results.", "", 2)
    return CheckResult("Structured Data", "Technical", "Passed",
                       f"{len(scripts)} structured data block(s) found.", f"{len(scripts)} JSON-LD", 2)


# ── Performance check ────────────────────────────────────────────────────────

def _check_load_speed(response_time_ms: float) -> CheckResult:
    ms = int(response_time_ms)
    if ms < 2000:
        return CheckResult("Page Load Speed", "Performance", "Passed",
                           f"Page loaded in {ms}ms — fast.", f"{ms}ms", 3)
    if ms < 4000:
        return CheckResult("Page Load Speed", "Performance", "Warning",
                           f"Page loaded in {ms}ms. Aim for under 2000ms.", f"{ms}ms", 3)
    return CheckResult("Page Load Speed", "Performance", "Failed",
                       f"Page loaded in {ms}ms — too slow. Optimize server response time.", f"{ms}ms", 3)


# ── Crawlability checks ──────────────────────────────────────────────────────

def _check_robots_meta(soup: BeautifulSoup) -> CheckResult:
    tag = soup.find("meta", attrs={"name": "robots"})
    if not tag:
        return CheckResult("Robots Meta Tag", "Crawlability", "Passed",
                           "No robots meta tag — page is indexable by default.", "indexable", 2)
    content = (tag.get("content") or "").lower()
    if "noindex" in content:
        return CheckResult("Robots Meta Tag", "Crawlability", "Failed",
                           f"Page has noindex directive. Search engines won't index this page.", content, 2)
    return CheckResult("Robots Meta Tag", "Crawlability", "Passed",
                       f"Robots directive '{content}' allows indexing.", content, 2)


async def _check_robots_txt(origin: str, client: httpx.AsyncClient) -> CheckResult:
    try:
        r = await client.get(f"{origin}/robots.txt", timeout=5.0, headers=_HEADERS)
        if r.status_code == 200:
            return CheckResult("robots.txt", "Crawlability", "Passed",
                               "robots.txt found and accessible.", f"{origin}/robots.txt", 2)
        return CheckResult("robots.txt", "Crawlability", "Warning",
                           f"robots.txt returned HTTP {r.status_code}.", f"{origin}/robots.txt", 2)
    except Exception:
        return CheckResult("robots.txt", "Crawlability", "Warning",
                           "Could not reach robots.txt.", f"{origin}/robots.txt", 2)


async def _check_sitemap(origin: str, client: httpx.AsyncClient) -> CheckResult:
    try:
        r = await client.get(f"{origin}/sitemap.xml", timeout=5.0, headers=_HEADERS)
        if r.status_code == 200:
            return CheckResult("Sitemap", "Crawlability", "Passed",
                               "sitemap.xml found and accessible.", f"{origin}/sitemap.xml", 2)
        return CheckResult("Sitemap", "Crawlability", "Warning",
                           "sitemap.xml not found. Create one to help search engines crawl your site.",
                           f"{origin}/sitemap.xml", 2)
    except Exception:
        return CheckResult("Sitemap", "Crawlability", "Warning",
                           "Could not reach sitemap.xml.", f"{origin}/sitemap.xml", 2)


async def _check_broken_links(soup: BeautifulSoup, base_url: str, client: httpx.AsyncClient) -> CheckResult:
    raw_hrefs = [a.get("href") for a in soup.find_all("a", href=True)]

    def is_checkable(href: str) -> bool:
        return bool(href) and not href.startswith(("mailto:", "tel:", "#", "javascript:", "data:"))

    seen: set = set()
    unique: list = []
    for href in raw_hrefs:
        if not is_checkable(href):
            continue
        full = urljoin(base_url, href)
        if full not in seen:
            seen.add(full)
            unique.append(full)
        if len(unique) >= 20:
            break

    if not unique:
        return CheckResult("Broken Links", "Crawlability", "Passed",
                           "No links found to check.", "0 links", 2)

    async def check_one(url: str) -> bool:
        try:
            r = await client.head(url, timeout=5.0, follow_redirects=True, headers=_HEADERS)
            if r.status_code == 405:
                r = await client.get(url, timeout=5.0, follow_redirects=True, headers=_HEADERS)
            return r.status_code >= 400
        except Exception:
            return True

    results = await asyncio.gather(*[check_one(u) for u in unique])
    broken = sum(results)

    if broken == 0:
        return CheckResult("Broken Links", "Crawlability", "Passed",
                           f"All {len(unique)} sampled link(s) are working.", f"0/{len(unique)} broken", 2)
    return CheckResult("Broken Links", "Crawlability", "Failed",
                       f"{broken} broken link(s) found out of {len(unique)} sampled.", f"{broken}/{len(unique)} broken", 2)


# ── Public API ───────────────────────────────────────────────────────────────

async def run_audit(html: str, url: str, response_time_ms: float) -> dict:
    soup = BeautifulSoup(html, "lxml")
    parsed = urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"

    shallow: List[CheckResult] = [
        _check_title(soup),
        _check_meta_description(soup),
        _check_canonical(soup),
        _check_og_title(soup),
        _check_og_description(soup),
        _check_og_image(soup),
        _check_twitter_card(soup),
        _check_h1(soup),
        _check_heading_hierarchy(soup),
        _check_word_count(soup),
        _check_image_alt(soup),
        _check_https(url),
        _check_viewport(soup),
        _check_favicon(soup),
        _check_language(soup),
        _check_structured_data(soup),
        _check_load_speed(response_time_ms),
        _check_robots_meta(soup),
    ]

    async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
        deep = list(await asyncio.gather(
            _check_robots_txt(origin, client),
            _check_sitemap(origin, client),
            _check_broken_links(soup, url, client),
        ))

    all_checks: List[CheckResult] = shallow + deep

    categories = []
    for cat_name in CATEGORY_ORDER:
        cat_checks = [c for c in all_checks if c.category == cat_name]
        if cat_checks:
            sorted_checks = sorted(cat_checks, key=lambda c: _STATUS_SORT[c.status])
            categories.append(CategoryResult(
                name=cat_name,
                score=_score(cat_checks),
                checks=sorted_checks,
            ))

    overall = _score(all_checks)
    passed = sum(1 for c in all_checks if c.status == "Passed")
    warned = sum(1 for c in all_checks if c.status == "Warning")
    failed = sum(1 for c in all_checks if c.status == "Failed")

    return {
        "url": url,
        "score": overall,
        "summary": _summary(overall, all_checks),
        "checks": [asdict(c) for c in all_checks],
        "categories": [
            {
                "name": cat.name,
                "score": cat.score,
                "checks": [asdict(c) for c in cat.checks],
            }
            for cat in categories
        ],
        "meta": asdict(AuditMeta(
            checks_total=len(all_checks),
            checks_passed=passed,
            checks_warned=warned,
            checks_failed=failed,
            response_time_ms=int(response_time_ms),
        )),
    }
```

- [ ] **Step 4: Run the tests**

```bash
cd /root/jana/projects/BoostSEO/SEO/backend
python -m pytest tests/test_seo_engine.py -v
```

Expected: all 9 tests pass. If a test fails, fix the specific check function it targets before moving on.

- [ ] **Step 5: Commit**

```bash
cd /root/jana/projects/BoostSEO
git add SEO/backend/app/services/seo_engine.py SEO/backend/tests/
git commit -m "feat: implement seo_engine with 21 checks and run_audit"
```

---

### Task 2: Slim down main.py — use seo_engine + update PDF

**Files:**
- Rewrite: `SEO/backend/app/main.py`

**Interfaces:**
- Consumes: `run_audit(html, url, response_time_ms)` from `app.services.seo_engine`
- Produces: `/analyze` GET endpoint returning the dict from `run_audit`; `/download-pdf` GET endpoint returning a PDF file

- [ ] **Step 1: Rewrite main.py**

Write `/root/jana/projects/BoostSEO/SEO/backend/app/main.py`:

```python
import time
import asyncio
from urllib.parse import urlparse

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

from app.services.seo_engine import run_audit

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

CATEGORY_ORDER = [
    "Meta & Social",
    "Content",
    "Technical",
    "Performance",
    "Crawlability",
]


async def _fetch_and_audit(url: str) -> dict:
    if not url.startswith("http"):
        url = "https://" + url
    async with httpx.AsyncClient(follow_redirects=True, timeout=20.0, headers=_HEADERS) as client:
        t0 = time.time()
        try:
            response = await client.get(url)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Connection failed: {e}")
        response_time_ms = (time.time() - t0) * 1000
    return await run_audit(response.text, str(response.url), response_time_ms)


@app.get("/analyze")
async def analyze_endpoint(url: str):
    return await _fetch_and_audit(url)


@app.get("/download-pdf")
async def download_pdf(url: str):
    data = await _fetch_and_audit(url)
    file_path = "SEO_Detailed_Report.pdf"
    _build_pdf(data, file_path)
    return FileResponse(file_path, filename="SEO_Report.pdf")


def _build_pdf(data: dict, file_path: str) -> None:
    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter
    score = data["score"]
    meta = data["meta"]

    # ── Header ──────────────────────────────────────────────────────────────
    c.setFont("Helvetica-Bold", 22)
    c.setFillColorRGB(0.1, 0.4, 0.7)
    c.drawString(50, height - 55, "BoostSEO — Technical SEO Report")

    c.setFont("Helvetica", 9)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawString(50, height - 72, f"URL: {data['url']}")
    c.drawString(50, height - 84, data["summary"])

    # score circle
    cx, cy, r = 510, height - 68, 38
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.circle(cx, cy, r, stroke=1, fill=0)
    c.setFont("Helvetica-Bold", 20)
    if score >= 70:
        c.setFillColorRGB(0, 0.6, 0.2)
    elif score >= 50:
        c.setFillColorRGB(0.7, 0.5, 0)
    else:
        c.setFillColorRGB(0.8, 0.1, 0.1)
    c.drawCentredString(cx, cy - 7, str(score))

    # stats row
    c.setFont("Helvetica", 9)
    c.setFillColorRGB(0, 0.55, 0.2)
    c.drawString(50, height - 100, f"✓ {meta['checks_passed']} Passed")
    c.setFillColorRGB(0.65, 0.45, 0)
    c.drawString(130, height - 100, f"⚠ {meta['checks_warned']} Warnings")
    c.setFillColorRGB(0.75, 0.1, 0.1)
    c.drawString(230, height - 100, f"✗ {meta['checks_failed']} Failed")
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawString(310, height - 100, f"Response: {meta['response_time_ms']}ms")

    # divider
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.line(50, height - 110, width - 50, height - 110)

    y = height - 128

    def check_page_break():
        nonlocal y
        if y < 60:
            c.showPage()
            y = height - 50

    # ── Category sections ────────────────────────────────────────────────────
    for cat in data["categories"]:
        check_page_break()

        # category header
        c.setFont("Helvetica-Bold", 11)
        c.setFillColorRGB(0.1, 0.4, 0.7)
        cat_score = cat["score"]
        c.drawString(50, y, f"{cat['name']}  —  {cat_score}%")
        c.line(50, y - 4, width - 50, y - 4)
        y -= 18

        # column headers
        c.setFont("Helvetica-Bold", 8)
        c.setFillColorRGB(0.3, 0.3, 0.3)
        c.drawString(50, y, "Check")
        c.drawString(180, y, "Status")
        c.drawString(250, y, "Message")
        y -= 14

        for check in cat["checks"]:
            check_page_break()
            c.setFont("Helvetica-Bold", 8)
            c.setFillColorRGB(0, 0, 0)
            c.drawString(50, y, check["name"][:22])

            status = check["status"]
            if status == "Passed":
                c.setFillColorRGB(0, 0.55, 0.2)
            elif status == "Warning":
                c.setFillColorRGB(0.65, 0.45, 0)
            else:
                c.setFillColorRGB(0.75, 0.1, 0.1)
            c.setFont("Helvetica-Bold", 8)
            c.drawString(180, y, status)

            c.setFillColorRGB(0.2, 0.2, 0.2)
            c.setFont("Helvetica", 8)
            msg = check["message"][:62]
            c.drawString(250, y, msg)
            y -= 14

        y -= 8  # spacing between categories

    c.save()
```

- [ ] **Step 2: Test the endpoint manually**

```bash
cd /root/jana/projects/BoostSEO/SEO/backend
pip install -r requirements.txt --quiet
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
sleep 3
curl -s "http://localhost:8000/analyze?url=https://example.com" | python3 -m json.tool | head -60
pkill -f "uvicorn app.main"
```

Expected: JSON with `url`, `score`, `summary`, `checks` (21 items), `categories` (5 groups), `meta`.

- [ ] **Step 3: Commit**

```bash
cd /root/jana/projects/BoostSEO
git add SEO/backend/app/main.py
git commit -m "feat: slim main.py to use seo_engine, update PDF for 21 checks"
```

---

### Task 3: Create CategoryCard.jsx

**Files:**
- Create: `SEO/frontend/src/CategoryCard.jsx`

**Interfaces:**
- Consumes: `category` prop with shape `{ name: string, score: number, checks: Array<{ name, category, status, message, value, weight }> }`
- Produces: collapsible card component used in Task 4

- [ ] **Step 1: Write CategoryCard.jsx**

Write `/root/jana/projects/BoostSEO/SEO/frontend/src/CategoryCard.jsx`:

```jsx
import { useState } from 'react';

const statusStyle = (status) => {
    if (status === 'Passed') return 'text-green-400 border-green-400/20 bg-green-400/10';
    if (status === 'Warning') return 'text-yellow-400 border-yellow-400/20 bg-yellow-400/10';
    return 'text-red-400 border-red-400/20 bg-red-400/10';
};

const scoreColor = (score) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 50) return 'text-yellow-400';
    return 'text-red-400';
};

const CategoryCard = ({ category }) => {
    const [expanded, setExpanded] = useState(true);

    return (
        <div className="bg-white/5 backdrop-blur-md rounded-2xl border border-white/10 overflow-hidden">
            <button
                onClick={() => setExpanded((v) => !v)}
                className="w-full flex justify-between items-center px-5 py-4 hover:bg-white/5 transition-colors text-left"
            >
                <div className="flex items-center gap-3">
                    <span className="text-white font-bold">{category.name}</span>
                    <span className={`text-sm font-bold ${scoreColor(category.score)}`}>
                        {category.score}%
                    </span>
                    <span className="text-gray-500 text-xs">
                        ({category.checks.filter(c => c.status === 'Failed').length} failed,{' '}
                        {category.checks.filter(c => c.status === 'Warning').length} warnings)
                    </span>
                </div>
                <span className="text-gray-400 text-xs">{expanded ? '▲' : '▼'}</span>
            </button>

            {expanded && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 px-4 pb-4">
                    {category.checks.map((check, i) => (
                        <div
                            key={i}
                            className="bg-white/5 p-4 rounded-xl border border-white/10 text-left hover:border-white/30 transition-colors"
                        >
                            <div className="flex justify-between items-start mb-2">
                                <span className="text-blue-400 text-xs uppercase tracking-widest font-bold leading-tight">
                                    {check.name}
                                </span>
                                <span className={`px-2 py-0.5 rounded text-[10px] font-bold border flex-shrink-0 ml-2 ${statusStyle(check.status)}`}>
                                    {check.status}
                                </span>
                            </div>
                            <p className="text-white font-medium text-sm mb-1">{check.message}</p>
                            {check.value && (
                                <p className="text-gray-500 text-xs truncate italic">Value: {check.value}</p>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default CategoryCard;
```

- [ ] **Step 2: Commit**

```bash
cd /root/jana/projects/BoostSEO
git add SEO/frontend/src/CategoryCard.jsx
git commit -m "feat: add CategoryCard component for grouped SEO results"
```

---

### Task 4: Update App.jsx — use categories + mini-score row

**Files:**
- Modify: `SEO/frontend/src/App.jsx`

**Interfaces:**
- Consumes: `data.categories`, `data.meta`, `data.score`, `data.summary` from API
- Consumes: `CategoryCard` component from Task 3

- [ ] **Step 1: Rewrite App.jsx**

Write `/root/jana/projects/BoostSEO/SEO/frontend/src/App.jsx`:

```jsx
import { useState } from 'react';
import axios from 'axios';
import { Routes, Route, Link } from 'react-router-dom';
import CategoryCard from './CategoryCard';
import PrivacyPolicy from './PrivacyPolicy';
import About from './About';
import Contact from './Contact';
import './App.css';

const AdBanner = () => (
    <ins
        className="adsbygoogle"
        style={{ display: 'block' }}
        data-ad-client="ca-pub-2280336108138157"
        data-ad-slot="8237171876"
        data-ad-format="auto"
        data-full-width-responsive="true"
        ref={(el) => {
            if (el) {
                try { (window.adsbygoogle = window.adsbygoogle || []).push({}); } catch (_) {}
            }
        }}
    />
);

const scoreRing = (score) => {
    if (score >= 70) return 'border-green-500 text-green-500';
    if (score >= 50) return 'border-yellow-500 text-yellow-500';
    return 'border-red-500 text-red-500';
};

const miniScoreColor = (score) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 50) return 'text-yellow-400';
    return 'text-red-400';
};

const Home = () => {
    const [url, setUrl] = useState('');
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleAnalyze = async () => {
        if (!url.trim()) return;
        setLoading(true);
        setError(null);
        setData(null);
        try {
            const response = await axios.get(`/api/analyze?url=${encodeURIComponent(url.trim())}`);
            setData(response.data);
        } catch (err) {
            setError('Unable to analyze the URL. Make sure it is publicly accessible and starts with https://');
        }
        setLoading(false);
    };

    return (
        <div className="relative min-h-screen w-full flex flex-col items-center overflow-x-hidden bg-[#020617]">
            <div className="stars"></div>
            <div className="twinkling"></div>

            {/* Hero / Tool */}
            <div className="relative z-10 w-full max-w-3xl px-4 mx-auto text-center pt-20 pb-10">
                <h1 className="text-4xl md:text-6xl font-extrabold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
                    BoostSEO
                </h1>
                <p className="text-gray-400 mb-2 text-sm md:text-lg">Free Technical SEO Audit — 21 Checks</p>
                <p className="text-gray-500 mb-8 text-xs md:text-sm max-w-xl mx-auto">
                    Enter any public URL to get an instant SEO health score, grouped check results, and a downloadable PDF report.
                </p>

                {/* Input */}
                <div className="flex flex-col md:flex-row gap-3 mb-8 shadow-2xl p-2 bg-white/5 backdrop-blur-md rounded-2xl border border-white/10">
                    <input
                        type="text"
                        placeholder="https://example.com"
                        className="flex-1 p-4 bg-transparent text-white outline-none placeholder-gray-500 text-lg"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
                    />
                    <button
                        onClick={handleAnalyze}
                        disabled={loading}
                        className="bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold py-3 px-8 rounded-xl transition-all hover:scale-105 active:scale-95 disabled:opacity-50"
                    >
                        {loading ? 'Analyzing…' : 'Start Audit'}
                    </button>
                </div>

                {error && (
                    <p className="text-red-400 mb-6 bg-red-400/10 p-3 rounded-lg border border-red-400/20">{error}</p>
                )}

                {/* Results */}
                {data && (
                    <div className="space-y-6 text-left animate-fadeIn">
                        {/* Overall score card */}
                        <div className="bg-white/10 backdrop-blur-xl p-8 rounded-3xl border border-white/20 shadow-2xl">
                            <div className="flex flex-col md:flex-row items-center justify-between gap-6">
                                <div>
                                    <h2 className="text-3xl font-bold text-white">Overall SEO Score</h2>
                                    <p className="text-gray-400 text-sm mt-1">Based on {data.meta.checks_total} checks</p>
                                    {data.summary && <p className="text-gray-300 text-sm mt-2">{data.summary}</p>}
                                    <div className="flex gap-5 mt-3 text-sm">
                                        <span className="text-green-400 font-medium">{data.meta.checks_passed} Passed</span>
                                        <span className="text-yellow-400 font-medium">{data.meta.checks_warned} Warnings</span>
                                        <span className="text-red-400 font-medium">{data.meta.checks_failed} Failed</span>
                                    </div>
                                </div>
                                <div className={`text-5xl font-black p-6 rounded-full border-4 flex-shrink-0 ${scoreRing(data.score)}`}>
                                    {data.score}
                                </div>
                            </div>

                            {/* Category mini-scores */}
                            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 border-t border-white/10 mt-6 pt-5">
                                {data.categories.map((cat) => (
                                    <div key={cat.name} className="text-center">
                                        <div className={`text-xl font-bold ${miniScoreColor(cat.score)}`}>{cat.score}%</div>
                                        <div className="text-gray-500 text-xs mt-1 leading-tight">{cat.name}</div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Category cards */}
                        {data.categories.map((cat) => (
                            <CategoryCard key={cat.name} category={cat} />
                        ))}

                        {/* Ad banner */}
                        <div className="rounded-2xl overflow-hidden">
                            <AdBanner />
                        </div>

                        {/* PDF download */}
                        <div className="flex justify-center pb-4">
                            <a
                                href={`/api/download-pdf?url=${encodeURIComponent(url)}`}
                                target="_blank"
                                rel="noreferrer"
                                className="bg-white/10 hover:bg-white/20 text-white px-6 py-3 rounded-xl border border-white/20 transition-all flex items-center gap-2"
                            >
                                📥 Download PDF Report
                            </a>
                        </div>
                    </div>
                )}

                {/* Feature grid — shown before first audit */}
                {!data && (
                    <div className="mt-12 grid grid-cols-1 sm:grid-cols-3 gap-4 text-left">
                        {[
                            { icon: '🏷️', label: 'Meta & Social', desc: 'Title, description, canonical, Open Graph, Twitter Card' },
                            { icon: '📝', label: 'Content', desc: 'H1/H2/H3 structure, word count, image alt text' },
                            { icon: '⚙️', label: 'Technical', desc: 'HTTPS, viewport, favicon, language, structured data' },
                            { icon: '⚡', label: 'Performance', desc: 'Page load speed vs 2-second benchmark' },
                            { icon: '🔍', label: 'Crawlability', desc: 'robots.txt, sitemap.xml, broken links' },
                            { icon: '📄', label: 'PDF Report', desc: 'Download a full audit report for any URL' },
                        ].map((item) => (
                            <div key={item.label} className="bg-white/5 backdrop-blur-md p-4 rounded-xl border border-white/10">
                                <div className="text-2xl mb-2">{item.icon}</div>
                                <p className="text-white font-semibold text-sm mb-1">{item.label}</p>
                                <p className="text-gray-400 text-xs">{item.desc}</p>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Footer */}
            <footer className="relative z-10 w-full py-6 text-center border-t border-white/5 bg-[#020617]/50 backdrop-blur-sm mt-auto">
                <div className="flex justify-center flex-wrap gap-6 text-sm">
                    <Link to="/" className="text-gray-500 hover:text-blue-400 transition-colors">Home</Link>
                    <Link to="/about" className="text-gray-500 hover:text-blue-400 transition-colors">About</Link>
                    <Link to="/contact" className="text-gray-500 hover:text-blue-400 transition-colors">Contact</Link>
                    <Link to="/privacy-policy" className="text-gray-500 hover:text-blue-400 transition-colors">Privacy Policy</Link>
                </div>
                <p className="mt-2 text-gray-600 text-xs">© 2026 BoostSEO. All rights reserved.</p>
            </footer>
        </div>
    );
};

function App() {
    return (
        <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/about" element={<About />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="/privacy-policy" element={<PrivacyPolicy />} />
        </Routes>
    );
}

export default App;
```

- [ ] **Step 2: Commit**

```bash
cd /root/jana/projects/BoostSEO
git add SEO/frontend/src/App.jsx
git commit -m "feat: update App.jsx with category groups and mini-score row"
```

---

### Task 5: Rebuild Docker containers and verify deployment

**Files:**
- No code changes — rebuild and redeploy existing containers

- [ ] **Step 1: Rebuild and restart the backend container**

```bash
cd /root/jana/projects/BoostSEO/SEO
docker compose build boostseo-backend
docker compose up -d boostseo-backend
```

Expected: build completes, container starts.

- [ ] **Step 2: Rebuild and restart the frontend container**

```bash
cd /root/jana/projects/BoostSEO/SEO
docker compose build boostseo-frontend
docker compose up -d boostseo-frontend
```

Expected: Vite build succeeds, nginx container starts on port 3012.

- [ ] **Step 3: Smoke-test the full stack through nginx**

```bash
sleep 8
curl -s "http://localhost:3012/api/analyze?url=https://example.com" | python3 -m json.tool | grep -E '"score"|"checks_total"'
```

Expected: `"score"` an integer and `"checks_total": 21`, confirming nginx proxy and new engine are working.

- [ ] **Step 4: Verify the live domain responds**

```bash
curl -s "https://boostseo.jxtechstudio.com/api/analyze?url=https://example.com" | python3 -m json.tool | grep -E '"score"|"checks_total"'
```

Expected: `"score"` and `"checks_total": 21` in the response.

- [ ] **Step 5: Final commit**

```bash
cd /root/jana/projects/BoostSEO
git add -A
git commit -m "chore: rebuild and deploy enhanced BoostSEO with 21 SEO checks"
```
