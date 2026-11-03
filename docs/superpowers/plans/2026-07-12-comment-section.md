# Comment Section Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a public feedback/comment section under the homepage feature grid, backed by a persistent SQLite store, where visitors submit name + email + comment, only the name and comment are ever shown publicly, and the site owner deletes unwanted comments by editing the SQLite file directly.

**Architecture:** A new `CommentsStore` class (`backend/app/services/comments_store.py`) wraps raw `sqlite3` access to a single `comments` table. A new FastAPI router (`backend/app/api/comments.py`) exposes `POST /comments` and `GET /comments`, validates input with Pydantic, rate-limits by IP in memory, and never returns the `email` field. `main.py` wires the router in. The frontend gets a new `CommentSection.jsx` component rendered under the feature grid in `Home` (`App.jsx`), styled to match the existing glass/dark theme, doing a `GET` on mount and a `POST` on submit via `/api/comments` (nginx strips the `/api` prefix, same as the existing `/api/analyze` → `/analyze` mapping). `docker-compose.yml` gets a named volume so the SQLite file survives container rebuilds.

**Tech Stack:** FastAPI + Pydantic v2 + stdlib `sqlite3` (backend, no new ORM), pytest + FastAPI `TestClient` (backend tests), React + axios + Tailwind (frontend, matching existing components).

## Global Constraints

- Email is collected but **never** returned by any API response or rendered anywhere in the frontend — it exists only in the SQLite file for the owner to read directly.
- Name, email, and body are all required; comments are auto-published immediately (no moderation queue, no delete endpoint) — deletion happens only via direct SQLite access on the server.
- Field length caps: `name` ≤ 100 chars, `email` ≤ 200 chars, `body` ≤ 2000 chars (from the spec).
- Per-IP rate limit: reject a second submission from the same IP within 30 seconds with `429`.
- The comment section only renders under the same condition as the existing feature grid in `Home` (i.e. before an audit has run / `!data`).
- Follow the existing code style in this repo: 4-space indentation, no semicolons-heavy style changes, Tailwind utility classes matching `CategoryCard.jsx` / `App.jsx` (`bg-white/5 backdrop-blur-md border border-white/10`, etc).

---

### Task 1: Comments data store (SQLite persistence layer)

**Files:**
- Create: `SEO/backend/app/services/comments_store.py`
- Modify: `SEO/backend/requirements.txt` (add `pytest`)
- Create: `SEO/backend/tests/test_comments_store.py`

**Interfaces:**
- Produces: `CommentsStore` class with:
  - `__init__(self, db_path: pathlib.Path = DEFAULT_DB_PATH)` — creates parent dir and the `comments` table if missing.
  - `insert_comment(self, name: str, email: str, body: str) -> dict` — returns `{"id": int, "name": str, "body": str, "created_at": str}` (no email).
  - `list_comments(self, limit: int = 100) -> list[dict]` — returns rows newest-first, same shape as above (no email), each dict has keys `id`, `name`, `body`, `created_at`.
  - Module constant `DEFAULT_DB_PATH: pathlib.Path` pointing at `<backend>/data/comments.db`.

- [ ] **Step 1: Add pytest to backend requirements**

Edit `SEO/backend/requirements.txt` to add a new line `pytest` (keep existing lines as-is):

```
fastapi
uvicorn
httpx
beautifulsoup4
lxml
python-dotenv
reportlab
pytest
```

- [ ] **Step 2: Create a Linux virtualenv for running backend tests**

The `SEO/backend/venv/` directory in this repo is a Windows venv (has `Lib`/`Scripts`, not `lib`/`bin`) and will not run on Linux. Create a separate, untracked venv instead:

```bash
cd SEO/backend
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

Expected: installs without error (fastapi, uvicorn, httpx, beautifulsoup4, lxml, python-dotenv, reportlab, pytest).

- [ ] **Step 3: Add `.venv` and `data/` to gitignore**

Edit `SEO/.gitignore`, add two lines at the end:

```
.venv/
data/
```

- [ ] **Step 4: Write the failing tests**

Create `SEO/backend/tests/test_comments_store.py`:

```python
from app.services.comments_store import CommentsStore


def test_insert_comment_returns_expected_shape_without_email(tmp_path):
    store = CommentsStore(tmp_path / "test.db")

    result = store.insert_comment("Jane", "jane@example.com", "Great tool!")

    assert result["name"] == "Jane"
    assert result["body"] == "Great tool!"
    assert "email" not in result
    assert isinstance(result["id"], int)
    assert "created_at" in result


def test_list_comments_returns_newest_first_without_email(tmp_path):
    store = CommentsStore(tmp_path / "test.db")
    store.insert_comment("Alice", "alice@example.com", "First comment")
    store.insert_comment("Bob", "bob@example.com", "Second comment")

    comments = store.list_comments()

    assert [c["name"] for c in comments] == ["Bob", "Alice"]
    assert all("email" not in c for c in comments)


def test_list_comments_respects_limit(tmp_path):
    store = CommentsStore(tmp_path / "test.db")
    for i in range(5):
        store.insert_comment(f"User{i}", f"user{i}@example.com", "Comment body")

    comments = store.list_comments(limit=2)

    assert len(comments) == 2


def test_store_creates_data_directory_and_table(tmp_path):
    db_path = tmp_path / "nested" / "comments.db"

    store = CommentsStore(db_path)

    assert db_path.parent.is_dir()
    assert store.list_comments() == []
```

- [ ] **Step 5: Run tests to verify they fail**

Run: `cd SEO/backend && ./.venv/bin/python -m pytest tests/test_comments_store.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.services.comments_store'` (module doesn't exist yet).

- [ ] **Step 6: Implement `CommentsStore`**

Create `SEO/backend/app/services/comments_store.py`:

```python
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "comments.db"


class CommentsStore:
    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_table()

    def _init_table(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    body TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def insert_comment(self, name: str, email: str, body: str) -> dict:
        created_at = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO comments (name, email, body, created_at) VALUES (?, ?, ?, ?)",
                (name, email, body, created_at),
            )
            conn.commit()
            comment_id = cursor.lastrowid
        return {"id": comment_id, "name": name, "body": body, "created_at": created_at}

    def list_comments(self, limit: int = 100) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT id, name, body, created_at FROM comments ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `cd SEO/backend && ./.venv/bin/python -m pytest tests/test_comments_store.py -v`
Expected: 4 passed.

- [ ] **Step 8: Commit**

```bash
cd SEO/backend
git add requirements.txt app/services/comments_store.py tests/test_comments_store.py
cd ..
git add .gitignore
git commit -m "feat: add SQLite-backed comments store"
```

---

### Task 2: Comments API endpoints

**Files:**
- Create: `SEO/backend/app/api/comments.py`
- Modify: `SEO/backend/app/main.py`
- Create: `SEO/backend/tests/test_comments_api.py`

**Interfaces:**
- Consumes: `CommentsStore` from Task 1 (`SEO/backend/app/services/comments_store.py`) — `insert_comment(name, email, body) -> dict`, `list_comments(limit=100) -> list[dict]`.
- Produces:
  - `router: fastapi.APIRouter` exported from `app/api/comments.py`, mounted in `main.py` via `app.include_router(comments_router)`.
  - `get_store() -> CommentsStore` dependency function, overridable in tests via `app.dependency_overrides`.
  - Routes: `POST /comments` (201 on success, 422 on invalid input, 429 on rate limit, 500 on unexpected store failure), `GET /comments` (200, list of comments).

- [ ] **Step 1: Write the failing API tests**

Create `SEO/backend/tests/test_comments_api.py`:

```python
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api import comments as comments_api
from app.services.comments_store import CommentsStore


@pytest.fixture
def client(tmp_path):
    test_store = CommentsStore(tmp_path / "test_comments.db")
    app.dependency_overrides[comments_api.get_store] = lambda: test_store
    comments_api._last_submission.clear()
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_valid_submission_returns_201_without_email(client):
    response = client.post(
        "/comments",
        json={"name": "Jane", "email": "jane@example.com", "body": "Great tool!"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Jane"
    assert data["body"] == "Great tool!"
    assert "email" not in data
    assert "id" in data
    assert "created_at" in data


def test_missing_field_returns_422(client):
    response = client.post(
        "/comments",
        json={"name": "Jane", "email": "jane@example.com"},
    )

    assert response.status_code == 422


def test_blank_field_returns_422(client):
    response = client.post(
        "/comments",
        json={"name": "   ", "email": "jane@example.com", "body": "Great tool!"},
    )

    assert response.status_code == 422


def test_malformed_email_returns_422(client):
    response = client.post(
        "/comments",
        json={"name": "Jane", "email": "not-an-email", "body": "Great tool!"},
    )

    assert response.status_code == 422


def test_body_too_long_returns_422(client):
    response = client.post(
        "/comments",
        json={"name": "Jane", "email": "jane@example.com", "body": "x" * 2001},
    )

    assert response.status_code == 422


def test_rapid_repeat_submission_returns_429(client):
    payload = {"name": "Jane", "email": "jane@example.com", "body": "Great tool!"}

    first = client.post("/comments", json=payload)
    second = client.post("/comments", json=payload)

    assert first.status_code == 201
    assert second.status_code == 429


def test_get_comments_never_includes_email(client):
    client.post(
        "/comments",
        json={"name": "Jane", "email": "jane@example.com", "body": "Nice!"},
    )

    response = client.get("/comments")

    assert response.status_code == 200
    comments = response.json()
    assert len(comments) == 1
    assert "email" not in comments[0]
    assert comments[0]["name"] == "Jane"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd SEO/backend && ./.venv/bin/python -m pytest tests/test_comments_api.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.api.comments'`.

- [ ] **Step 3: Implement the comments router**

Create `SEO/backend/app/api/comments.py`:

```python
import re
import time

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, field_validator

from app.services.comments_store import CommentsStore

router = APIRouter()

RATE_LIMIT_SECONDS = 30
_last_submission: dict[str, float] = {}

_store = CommentsStore()

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def get_store() -> CommentsStore:
    return _store


class CommentIn(BaseModel):
    name: str = Field(..., max_length=100)
    email: str = Field(..., max_length=200)
    body: str = Field(..., max_length=2000)

    @field_validator("name", "email", "body")
    @classmethod
    def not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must not be empty")
        return v

    @field_validator("email")
    @classmethod
    def valid_email_shape(cls, v: str) -> str:
        if not _EMAIL_RE.match(v):
            raise ValueError("must be a valid email address")
        return v


class CommentOut(BaseModel):
    id: int
    name: str
    body: str
    created_at: str


@router.post("/comments", status_code=201, response_model=CommentOut)
def create_comment(
    payload: CommentIn,
    request: Request,
    store: CommentsStore = Depends(get_store),
) -> dict:
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    last = _last_submission.get(client_ip)
    if last is not None and now - last < RATE_LIMIT_SECONDS:
        raise HTTPException(status_code=429, detail="Please wait before commenting again.")

    try:
        comment = store.insert_comment(payload.name, payload.email, payload.body)
    except Exception:
        raise HTTPException(status_code=500, detail="Could not save comment.")

    _last_submission[client_ip] = now
    return comment


@router.get("/comments", response_model=list[CommentOut])
def get_comments(store: CommentsStore = Depends(get_store)) -> list[dict]:
    return store.list_comments()
```

- [ ] **Step 4: Wire the router into `main.py`**

Modify `SEO/backend/app/main.py` — add the import near the top (after the existing `from app.services.seo_engine import run_audit` line) and register the router after the CORS middleware block:

```python
from app.services.seo_engine import run_audit
from app.api.comments import router as comments_router
```

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(comments_router)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd SEO/backend && ./.venv/bin/python -m pytest tests/ -v`
Expected: all tests pass, including the Task 1 store tests and the existing `test_seo_engine.py` tests (unaffected).

- [ ] **Step 6: Commit**

```bash
cd SEO/backend
git add app/api/comments.py app/main.py tests/test_comments_api.py
git commit -m "feat: add comments API endpoints with rate limiting"
```

---

### Task 3: Persistent storage volume for deployment

**Files:**
- Modify: `SEO/docker-compose.yml`

**Interfaces:**
- Consumes: `DEFAULT_DB_PATH` from Task 1, which resolves to `/app/data/comments.db` inside the container (since the Dockerfile's `WORKDIR` is `/app` and copies `backend/app` to `./app`, making `Path(__file__).resolve().parent.parent.parent` equal to `/app`).
- Produces: a named Docker volume `boostseo-comments-data` mounted at `/app/data` in the `boostseo-backend` service, so comments survive container rebuilds/restarts.

- [ ] **Step 1: Add the volume to `docker-compose.yml`**

Modify `SEO/docker-compose.yml`:

```yaml
version: "3.9"

services:
  boostseo-backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    container_name: boostseo-backend
    restart: unless-stopped
    expose:
      - "8000"
    volumes:
      - boostseo-comments-data:/app/data

  boostseo-frontend:
    build:
      context: ./frontend
    container_name: boostseo-frontend
    restart: unless-stopped
    ports:
      - "3012:80"
    depends_on:
      - boostseo-backend

volumes:
  boostseo-comments-data:
```

- [ ] **Step 2: Validate the compose file**

Run: `cd SEO && docker compose config --quiet`
Expected: no output, exit code 0 (confirms valid YAML and schema).

- [ ] **Step 3: Commit**

```bash
cd SEO
git add docker-compose.yml
git commit -m "feat: persist comments across backend container rebuilds"
```

---

### Task 4: Frontend comment section UI

**Files:**
- Create: `SEO/frontend/src/CommentSection.jsx`
- Modify: `SEO/frontend/src/App.jsx:206-219`

**Interfaces:**
- Consumes: `GET /api/comments` → `[{id, name, body, created_at}, ...]`; `POST /api/comments` with `{name, email, body}` → `{id, name, body, created_at}` on success (201), or throws with `err.response.status` of `422`/`429` on failure — matches Task 2's `CommentOut`/`CommentIn` shapes exactly.
- Produces: default-exported `CommentSection` component, rendered with no props, placed directly below the feature grid inside the existing `{!data && (...)}` block in `Home`.

- [ ] **Step 1: Create the `CommentSection` component**

Create `SEO/frontend/src/CommentSection.jsx`:

```jsx
import { useEffect, useState } from 'react';
import axios from 'axios';

const isValidEmail = (value) => /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(value);

const CommentSection = () => {
    const [comments, setComments] = useState([]);
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [body, setBody] = useState('');
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        axios.get('/api/comments')
            .then((res) => setComments(res.data))
            .catch(() => {});
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);

        const trimmedName = name.trim();
        const trimmedEmail = email.trim();
        const trimmedBody = body.trim();

        if (!trimmedName || !trimmedEmail || !trimmedBody) {
            setError('Please fill in your name, email, and comment.');
            return;
        }
        if (!isValidEmail(trimmedEmail)) {
            setError('Please enter a valid email address.');
            return;
        }

        setSubmitting(true);
        try {
            const response = await axios.post('/api/comments', {
                name: trimmedName,
                email: trimmedEmail,
                body: trimmedBody,
            });
            setComments((prev) => [response.data, ...prev]);
            setName('');
            setEmail('');
            setBody('');
        } catch (err) {
            if (err.response?.status === 429) {
                setError('Please wait a bit before submitting another comment.');
            } else {
                setError('Unable to submit your comment. Please try again.');
            }
        }
        setSubmitting(false);
    };

    return (
        <div className="mt-12 text-left">
            <h2 className="text-2xl font-bold text-white mb-4">What people think</h2>

            <form
                onSubmit={handleSubmit}
                className="bg-white/5 backdrop-blur-md p-5 rounded-xl border border-white/10 mb-6 space-y-3"
            >
                <div className="flex flex-col md:flex-row gap-3">
                    <input
                        type="text"
                        placeholder="Your name"
                        className="flex-1 p-3 bg-white/5 text-white rounded-lg border border-white/10 outline-none placeholder-gray-500"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                    />
                    <input
                        type="email"
                        placeholder="Your email (kept private)"
                        className="flex-1 p-3 bg-white/5 text-white rounded-lg border border-white/10 outline-none placeholder-gray-500"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                    />
                </div>
                <textarea
                    placeholder="What do you think of BoostSEO?"
                    className="w-full p-3 bg-white/5 text-white rounded-lg border border-white/10 outline-none placeholder-gray-500 min-h-24"
                    value={body}
                    onChange={(e) => setBody(e.target.value)}
                />
                {error && (
                    <p className="text-red-400 bg-red-400/10 p-3 rounded-lg border border-red-400/20 text-sm">
                        {error}
                    </p>
                )}
                <button
                    type="submit"
                    disabled={submitting}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold py-2 px-6 rounded-xl transition-all hover:scale-105 active:scale-95 disabled:opacity-50"
                >
                    {submitting ? 'Submitting…' : 'Submit Comment'}
                </button>
            </form>

            <div className="space-y-3">
                {comments.map((c) => (
                    <div key={c.id} className="bg-white/5 p-4 rounded-xl border border-white/10">
                        <div className="flex justify-between items-baseline mb-1">
                            <span className="text-white font-semibold text-sm">{c.name}</span>
                            <span className="text-gray-500 text-xs">
                                {new Date(c.created_at).toLocaleDateString()}
                            </span>
                        </div>
                        <p className="text-gray-300 text-sm">{c.body}</p>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default CommentSection;
```

- [ ] **Step 2: Wire it into `Home`**

Modify `SEO/frontend/src/App.jsx`. Add the import at the top, alongside the other component imports (after `import CategoryCard from './CategoryCard';`):

```jsx
import CategoryCard from './CategoryCard';
import CommentSection from './CommentSection';
```

Then, inside the `{!data && (...)}` block (`SEO/frontend/src/App.jsx:207-219`), add `<CommentSection />` directly after the closing `</div>` of the feature grid, still inside the same conditional:

```jsx
                {/* Feature grid — shown before first audit */}
                {!data && (
                    <div className="mt-12 grid grid-cols-1 sm:grid-cols-3 gap-4 text-left">
                        {FEATURE_CARDS.map((item) => (
                            <div key={item.label} className="bg-white/5 backdrop-blur-md p-5 rounded-xl border border-white/10">
                                <div className="w-9 h-9 rounded-lg bg-blue-500/15 flex items-center justify-center mb-3">
                                    <item.Icon className="w-5 h-5 text-blue-400" />
                                </div>
                                <p className="text-white font-semibold text-sm mb-1">{item.label}</p>
                                <p className="text-gray-400 text-xs leading-relaxed">{item.desc}</p>
                            </div>
                        ))}
                    </div>
                )}

                {/* Comment section — shown before first audit */}
                {!data && <CommentSection />}
```

- [ ] **Step 3: Commit**

```bash
cd SEO/frontend
git add src/CommentSection.jsx src/App.jsx
git commit -m "feat: add public comment section under the feature grid"
```

---

### Task 5: End-to-end manual verification

**Files:** none (verification only)

**Interfaces:**
- Consumes: the full stack from Tasks 1–4.

- [ ] **Step 1: Start the backend**

```bash
cd SEO/backend
./.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Expected: server starts without error, logs `Uvicorn running on http://0.0.0.0:8000`.

- [ ] **Step 2: Exercise the API directly**

In a second terminal:

```bash
curl -s -X POST http://localhost:8000/comments \
  -H "Content-Type: application/json" \
  -d '{"name":"Jane","email":"jane@example.com","body":"Loving BoostSEO!"}' | python3 -m json.tool

curl -s http://localhost:8000/comments | python3 -m json.tool
```

Expected: POST returns 201 with `id`, `name`, `body`, `created_at` and **no** `email` key; GET returns a list containing that comment, also without `email`.

- [ ] **Step 3: Confirm the email is only in the SQLite file**

```bash
sqlite3 SEO/backend/data/comments.db "SELECT id, name, email, body FROM comments;"
```

Expected: the row is present with the real email address, confirming it's stored for contact purposes but was never exposed over the API.

- [ ] **Step 4: Start the frontend dev server and exercise the UI in-browser**

```bash
cd SEO/frontend
npm install
npm run dev
```

Open the printed local URL in a browser (note: the Vite dev server has no `/api` proxy configured, so either run the app through the built Docker/nginx stack for a true end-to-end check, or temporarily point axios at `http://localhost:8000` while testing standalone). Verify:
- The comment section renders under the feature grid before running an audit.
- Submitting with a blank field shows the inline validation error and does not call the API.
- Submitting with a malformed email shows the inline validation error.
- A valid submission clears the form and the new comment appears immediately at the top of the list with the name and body visible, and no email anywhere on the page.
- Submitting twice in a row quickly shows the rate-limit error message.
- Running an audit (Start Audit) hides both the feature grid and the comment section, exactly like today's behavior with the grid alone.

- [ ] **Step 5: Verify via the real Docker/nginx stack (matches production routing)**

```bash
cd SEO
docker compose up --build
```

Open `http://localhost:3012`, repeat the checks from Step 4 through the nginx-proxied `/api/comments` path (this is the path real users hit). Confirm comments persist after `docker compose restart boostseo-backend`.

- [ ] **Step 6: Report results**

Summarize pass/fail for each check above before considering the feature complete. If any check fails, return to the relevant task and fix before proceeding.
