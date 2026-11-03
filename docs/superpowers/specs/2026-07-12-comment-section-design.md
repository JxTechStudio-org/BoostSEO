# Comment Section Design

## Purpose

Add a public feedback/comment section to the BoostSEO homepage, below the feature grid (shown only before the user runs an audit, same condition as the grid). Goal: collect visitor opinions on the site now that it has traffic, while capturing an email for follow-up contact — without exposing that email publicly.

## Data model

Single SQLite database (`comments.db`), accessed via Python's stdlib `sqlite3` (no ORM needed for one table). One table:

```sql
CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TEXT NOT NULL   -- ISO 8601 UTC timestamp
);
```

- No soft-delete flag, no moderation-status column. Comments are auto-published immediately on submission.
- Moderation is reactive: the site owner deletes bad rows directly with `sqlite3` / `DELETE FROM comments WHERE id = ...` on the server. No admin UI or delete endpoint is built.
- Email is stored so the owner can contact the commenter later, but it is never returned by any API endpoint or rendered in the frontend.

## Persistence

The backend currently has no volume mount at all (`SEO/docker-compose.yml`), so any file written inside the container is lost on rebuild/restart. Add a named volume:

```yaml
boostseo-backend:
  ...
  volumes:
    - boostseo-comments-data:/app/data

volumes:
  boostseo-comments-data:
```

The sqlite file lives at `/app/data/comments.db` inside the container (mapped to the named volume), referenced from a `DATA_DIR`-style path in the backend code.

## API endpoints

New module `backend/app/api/comments.py`, included into `backend/app/main.py`.

### `POST /api/comments`

Request body: `{ "name": str, "email": str, "body": str }`

Validation (server-side, in addition to client-side checks):
- All three fields required and non-empty after trimming whitespace.
- Length caps: `name` ≤ 100 chars, `email` ≤ 200 chars, `body` ≤ 2000 chars.
- `email` must match a basic email shape (regex), not deliverability-checked.
- Basic per-IP rate limit: reject with 429 if the same IP posted within the last 30 seconds. Implemented as an in-memory dict of `ip -> last_submit_time` (acceptable to reset on restart at this scale — no Redis/external store needed).

Responses:
- `201` with `{ id, name, body, created_at }` (no email) on success.
- `422` with a clear validation message for bad input.
- `429` with a "please wait before commenting again" message when rate-limited.
- `500` generic message on unexpected DB failure (no internal details leaked).

### `GET /api/comments`

Returns the latest comments, newest first, capped at 100 rows: `[{ id, name, body, created_at }, ...]`. Email is never included in this or any other response.

## Frontend

New component `SEO/frontend/src/CommentSection.jsx`, rendered in `Home` (`App.jsx`) directly under the feature grid, under the same `{!data && (...)}` condition so it only shows before an audit runs.

- Styled consistently with the existing glassmorphic dark theme (`bg-white/5 backdrop-blur-md border border-white/10`, etc.) already used throughout `Home`.
- Form fields: Name (text input), Email (text input), Comment (textarea), Submit button.
- Client-side validation mirrors the server: required fields, basic email pattern, before firing the request.
- On submit: `POST /api/comments`; on success, prepend the returned comment to the in-memory list (no refetch) and clear the form; on error, show an inline message reusing the existing red error-banner style.
- On mount: `GET /api/comments` to populate the list.
- Each rendered comment shows: name, a short/relative date, and the comment body. No email is ever rendered.

## Error handling

- Backend errors return the status codes and messages above; nothing internal (stack traces, DB paths) is exposed to the client.
- Frontend errors (validation, network, rate limit) surface inline near the comment form only — they do not affect the rest of the page (grid, Start Audit flow, existing results view remain fully functional regardless of comment section state).

## Testing

- Backend (`backend/tests/`): new test file covering
  - valid submission persists a row and the response excludes email
  - missing/empty required field → 422
  - malformed email → 422
  - rapid repeat submission from the same client → second request gets 429
  - `GET /api/comments` never includes the email field
- Frontend: no existing test harness in this repo; verified manually by running the dev server and exercising submit success, validation errors, and the rate-limit error path in-browser before marking the work done.

## Out of scope

- No admin UI/API for viewing or deleting comments — direct sqlite access only.
- No pre-publication moderation/approval queue — comments are live immediately.
- No pagination beyond the 100-row cap (acceptable at current traffic; revisit if volume grows).
