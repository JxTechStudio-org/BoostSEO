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
                           "Page has noindex directive. Search engines won't index this page.", content, 2)
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
