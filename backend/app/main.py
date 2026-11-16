"""BoostSEO API application setup.

Wires together the CORS middleware and the feature routers. All endpoint
logic lives in ``app.api`` and all business logic in ``app.services`` so this
module stays a thin composition root.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analyze import router as analyze_router
from app.api.comments import router as comments_router

app = FastAPI(title="BoostSEO API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router)
app.include_router(comments_router)
