import re
import time
from datetime import datetime, timezone

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


def _client_ip(request: Request) -> str:
    # X-Real-IP is set by nginx via `proxy_set_header X-Real-IP $remote_addr;`,
    # which always overwrites any client-supplied value with the true socket
    # peer address, so it cannot be spoofed. Trust it first.
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    # X-Forwarded-For is set via `proxy_set_header X-Forwarded-For
    # $proxy_add_x_forwarded_for;`, which *appends* to any incoming value
    # rather than overwriting it. A client can prepend arbitrary values, so
    # only the last hop (added by our own nginx) can be trusted here. This is
    # a fallback in case X-Real-IP is ever absent.
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[-1].strip()
    return request.client.host if request.client else "unknown"


class CommentIn(BaseModel):
    name: str = Field(..., max_length=100)
    email: str = Field(..., max_length=200)
    body: str = Field(..., max_length=2000)
    website: str = Field(default="", max_length=200)

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
    # Honeypot: this field is invisible to real visitors, so only bots that
    # blindly auto-fill every form input will populate it. Return a
    # normal-looking success response (same shape/status as a real comment)
    # without touching the store or the rate limiter, and without logging or
    # persisting anything about the attempt — a bot that sees a convincing
    # fake success has no signal it was caught, so it won't adapt.
    if payload.website.strip():
        return {
            "id": 0,
            "name": payload.name,
            "body": payload.body,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    client_ip = _client_ip(request)
    now = time.time()

    # Prune expired entries so _last_submission doesn't grow unbounded over
    # the life of the process, one entry per distinct IP ever seen.
    expired = [
        ip for ip, ts in _last_submission.items() if now - ts >= RATE_LIMIT_SECONDS
    ]
    for ip in expired:
        del _last_submission[ip]

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
