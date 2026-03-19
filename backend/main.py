"""FastAPI entry point for the Prompt Engineering System v2."""

import os
import sys

# Fix Windows GBK encoding — AIhub responses contain emoji (📌 etc.)
# which crash the SSE stream under default GBK codec.
os.environ.setdefault("PYTHONUTF8", "1")
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add backend dir to path so `services.xxx` imports work
sys.path.insert(0, os.path.dirname(__file__))

# Load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"[Config] Loaded .env from {env_path}")
except ImportError:
    pass  # dotenv not installed, rely on system env vars

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import init_db
from routers import chat, dimensions

# Log AIhub config on import
import services.aihub_client as _aihub
print(f"[AIhub] API URL: {_aihub.AIHUB_API_URL}")
print(f"[AIhub] Chatflow Bot ID: {_aihub.AIHUB_BOT_ID or '⚠️ NOT SET'}")
print(f"[AIhub] Workflow Bot ID: {_aihub.AIHUB_WORKFLOW_BOT_ID or '⚠️ NOT SET'}")
print(f"[AIhub] Analyze Bot ID: {_aihub.AIHUB_ANALYZE_BOT_ID or '⚠️ NOT SET'}")
print(f"[AIhub] BTS App: {_aihub.BTS_APP_NAME}")


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


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "prompt-engineering-v2"}


# Demo page route - MUST be before SPA catch-all route
@app.get("/demo")
async def demo_page():
    """Serve AI Employee Demo page"""
    from fastapi.responses import FileResponse
    demo_path = os.path.join(os.path.dirname(__file__), "static", "ai-employee-demo.html")
    if os.path.exists(demo_path):
        return FileResponse(demo_path)
    return {"error": "Demo page not found"}


# Static files — MUST be after all API routes
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
index_path = os.path.join(static_dir, "index.html")

if os.path.exists(index_path):
    from fastapi.responses import FileResponse

    # Serve static assets (js, css, images)
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")

    # SPA fallback: any non-API path returns index.html
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # If file exists in static dir, serve it
        file_path = os.path.join(static_dir, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        # Otherwise return index.html for SPA routing
        return FileResponse(index_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
