"""FastAPI entry point for the Prompt Engineering Dimension Platform."""

import os
import sys

# Fix Windows GBK encoding
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

# Add backend dir to path
sys.path.insert(0, os.path.dirname(__file__))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from routers import chat, dimensions

# Check database type
DATABASE_URL = os.environ.get("DATABASE_URL")
USE_POSTGRES = DATABASE_URL and DATABASE_URL.startswith("postgresql")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Simple lifespan - no blocking init."""
    print(f"[Startup] Starting with {'PostgreSQL' if USE_POSTGRES else 'SQLite'}")
    yield
    print("[Shutdown] Shutting down")


app = FastAPI(
    title="提示词工程维度管理平台",
    description="Prompt Engineering Dimension Platform — 111 个维度管理",
    version="2.1.0",
    lifespan=lifespan,
)

# CORS
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
    return {"status": "ok"}


@app.get("/")
async def root():
    return {
        "service": "提示词工程维度管理平台",
        "version": "2.1.0",
        "endpoints": {
            "/api/health": "Health check",
            "/api/dimensions": "List dimensions",
            "/api/dimensions/categories": "List categories"
        }
    }


# Static files
static_dir = "/app/static"
os.makedirs(static_dir, exist_ok=True)
index_path = os.path.join(static_dir, "index.html")

if os.path.exists(index_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets"), html=True), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api/"):
            return JSONResponse({"error": "Not found"}, status_code=404)
        file_path = os.path.join(static_dir, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(index_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
