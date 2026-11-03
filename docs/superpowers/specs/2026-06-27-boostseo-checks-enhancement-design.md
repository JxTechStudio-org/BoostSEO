# BoostSEO — Expanded SEO Checks Enhancement

**Date:** 2026-06-27  
**Status:** Approved  
**Scope:** Backend check expansion (6 → 21 checks) + frontend grouped results UI

---

## Goal

Expand BoostSEO from 6 basic checks to 21 thorough checks covering meta/social tags, content quality, technical SEO, performance, and crawlability. Group results by category in the UI with failed/warning checks surfaced first within each group.

---

## Backend Architecture

### seo_engine.py (activated)

The currently unused `services/seo_engine.py` becomes the single source of truth for all check logic. `main.py` is reduced to HTTP fetching and calling the engine.

**Public interface:**
```python
async def run_audit(html: str, url: str, response_time_ms: float) -> AuditResult
```

**CheckResult dataclass:**
```python
@dataclass
class CheckResult:
    name: str
    category: str        # "Meta & Social" | "Content" | "Technical" | "Performance" | "Crawlability"
    status: str          # "Passed" | "Warning" | "Failed"
    message: str
    value: str
    weight: int          # 1 (nice-to-have) | 2 (important) | 3 (critical)
```

**AuditResult dataclass:**
```python
@dataclass
class AuditResult:
    url: str
    score: int
    summary: str
    checks: list[CheckResult]       # flat list (for PDF)
    categories: list[CategoryResult]  # grouped (for UI)
    meta: AuditMeta
```

**CategoryResult dataclass:**
```python
@dataclass
class CategoryResult:
    name: str
    score: int           # category-level score 0-100
    checks: list[CheckResult]  # sorted: Failed → Warning → Passed
```

**AuditMeta dataclass:**
```python
@dataclass
class AuditMeta:
    checks_total: int
    checks_passed: int
    checks_warned: int
    checks_failed: int
    response_time_ms: int
```

### Check Functions

Each check is a private function in `seo_engine.py`:

```python
def _check_name(html, url, ...) -> CheckResult:
    ...
```

### Checks by Category

#### Meta & Social (7 checks)
| Check | Weight | Pass Condition |
|---|---|---|
| Title Tag | 3 | Present, 10–60 chars |
| Meta Description | 3 | Present |
| Canonical URL | 2 | `<link rel="canonical">` present |
| Open Graph Title | 2 | `og:title` present |
| Open Graph Description | 1 | `og:description` present |
| Open Graph Image | 1 | `og:image` present |
| Twitter Card | 1 | `twitter:card` present |

#### Content (4 checks)
| Check | Weight | Pass Condition |
|---|---|---|
| H1 Heading | 3 | Exactly one H1 |
| Heading Hierarchy | 2 | Pass: ≥1 H2 present; Warning: no H2 but H3+ present; Failed: no subheadings at all |
| Word Count | 2 | Pass: ≥300 words; Warning: 100–299 words; Failed: <100 words |
| Image Alt Text | 2 | All images have alt text |

#### Technical (5 checks)
| Check | Weight | Pass Condition |
|---|---|---|
| HTTPS | 3 | URL starts with https:// |
| Viewport Meta Tag | 2 | `<meta name="viewport">` present |
| Favicon | 1 | `<link rel="icon">` present |
| Language Attribute | 1 | `<html lang="...">` present |
| Structured Data | 2 | JSON-LD `<script type="application/ld+json">` present |

#### Performance (1 check)
| Check | Weight | Pass Condition |
|---|---|---|
| Page Load Speed | 3 | Response time < 2000ms |

#### Crawlability (4 checks)
| Check | Weight | Pass Condition |
|---|---|---|
| Robots Meta Tag | 2 | Pass: tag absent (default indexable) or present without `noindex`; Failed: `noindex` found |
| robots.txt | 2 | GET `{origin}/robots.txt` returns 200 |
| Sitemap | 2 | GET `{origin}/sitemap.xml` returns 200 |
| Broken Links | 2 | All sampled links return non-4xx (cap: 20 links) |

### Scoring

```
score = round(sum(earned_points) / sum(all_weights) * 100)
```

Where `earned_points` for a check = `weight` if Passed, `weight / 2` if Warning, `0` if Failed.

Category score uses the same formula applied only to that category's checks.

### Deep Checks (Crawlability)

robots.txt, sitemap.xml, and broken link checks require additional HTTP requests. These run concurrently via `asyncio.gather` after the main page fetch completes. Broken links are capped at 20 unique href values sampled from the page. Each deep check has a 5-second individual timeout.

### main.py Changes

`main.py` is reduced to:
1. Validate and normalize URL
2. Fetch page HTML + measure response time via HTTPX
3. Call `await seo_engine.run_audit(html, url, response_time_ms)`
4. Return serialized `AuditResult`
5. PDF endpoint updated to render all 21 checks grouped by category

---

## API Response

### GET /analyze?url=

```json
{
  "url": "https://example.com",
  "score": 74,
  "summary": "Good SEO foundation. Fix 3 critical issues to improve ranking.",
  "checks": [
    {
      "name": "Title Tag",
      "category": "Meta & Social",
      "status": "Passed",
      "message": "Title is 52 characters — within the optimal range.",
      "value": "Example Domain | Home",
      "weight": 3
    }
  ],
  "categories": [
    {
      "name": "Meta & Social",
      "score": 60,
      "checks": []
    }
  ],
  "meta": {
    "checks_total": 21,
    "checks_passed": 14,
    "checks_warned": 4,
    "checks_failed": 3,
    "response_time_ms": 843
  }
}
```

- `checks` — flat list, used by PDF generation (no breaking change)
- `categories` — grouped + sorted list, used by the new frontend UI
- Each category's `checks` are sorted: Failed → Warning → Passed

---

## Frontend

### New Component: CategoryCard.jsx

```
CategoryCard
├── Header: category name + mini-score badge + collapse toggle
└── Check list (sorted: Failed → Warning → Passed)
    └── Existing check card markup (no style change)
```

State: `isExpanded` (default: true). Toggle on header click.

### Results Layout (after audit)

```
┌─────────────────────────────────────────┐
│  Overall Score: 74                      │
│  Meta&Social  Content  Tech  Perf  Crawl│
│     60%        90%     45%   80%   33%  │
└─────────────────────────────────────────┘

┌─ Meta & Social ── 60% ──────── [collapse]┐
│  ✗ Canonical URL — not found             │
│  ⚠ Open Graph Image — missing            │
│  ✓ Title Tag — 52 chars, optimal         │
│  ...                                     │
└──────────────────────────────────────────┘

┌─ Content ── 90% ────────────── [collapse]┐
│  ...                                     │
└──────────────────────────────────────────┘

[ ad banner ]

[ Download PDF Report ]
```

### App.jsx Changes

- Import and render `CategoryCard` per entry in `data.categories`
- Add category mini-score row to the score card
- Remove the old flat `checks` grid (replaced by `CategoryCard` list)
- Keep PDF download button and ad banner placement unchanged

### Files Changed

| File | Change |
|---|---|
| `backend/app/services/seo_engine.py` | Full rewrite — all check logic lives here |
| `backend/app/main.py` | Slim down — fetch + call engine + return result |
| `frontend/src/App.jsx` | Use `data.categories`, add mini-score row, render `CategoryCard` |
| `frontend/src/CategoryCard.jsx` | New component |

---

## Out of Scope

- User accounts or audit history (Phase B)
- Keyword density analysis
- Core Web Vitals (requires headless browser)
- Email reports
