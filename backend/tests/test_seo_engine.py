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
    result = run(run_audit(NO_TITLE_HTML, "https://example.com", 800.0))
    order = {"Failed": 0, "Warning": 1, "Passed": 2}
    for cat in result["categories"]:
        statuses = [c["status"] for c in cat["checks"]]
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
