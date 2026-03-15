"""FastAPI entry point for the Prompt Engineering System v2."""

import os
import sys

# Add backend dir to path so `services.xxx` imports work
sys.path.insert(0, os.path.dirname(__file__))

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import init_db
from routers import chat, dimensions, engines, match, prompt, review, stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    yield


app = FastAPI(
    title="华渔提示词工程 · AI设计师",
    description="Prompt Engineering System v2 — 信息对称 · 相信 AI",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS — allow localhost on any port during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(chat.router)
app.include_router(dimensions.router)
app.include_router(review.router)
app.include_router(match.router)
app.include_router(prompt.router)
app.include_router(engines.router)
app.include_router(stats.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "prompt-engineering-v2"}


# Static files — MUST be after all API routes
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
# Only mount if index.html exists (to avoid errors during API-only development)
index_path = os.path.join(static_dir, "index.html")
if os.path.exists(index_path):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
