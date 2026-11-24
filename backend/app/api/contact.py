"""Contact form endpoint: receive a visitor's message and email it to the team."""
import re

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from app.services.email_sender import EmailNotConfigured, send_contact_email

router = APIRouter()

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ContactIn(BaseModel):
    email: str = Field(..., max_length=200)
    message: str = Field(..., max_length=5000)
    # Honeypot: hidden from real visitors, so only bots fill it in (same approach
    # as the comments endpoint). A filled value is silently treated as success.
    website: str = Field(default="", max_length=200)

    @field_validator("email", "message")
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


@router.post("/contact")
def send_contact_message(payload: ContactIn) -> dict:
    # Honeypot filled → pretend it worked and send nothing (no signal to the bot).
    if payload.website.strip():
        return {"status": "sent"}
    try:
        send_contact_email(payload.email, payload.message)
    except EmailNotConfigured:
        raise HTTPException(status_code=503, detail="Email service is unavailable.")
    except Exception:
        raise HTTPException(status_code=502, detail="Could not send the message.")
    return {"status": "sent"}
