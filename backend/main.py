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

# Add backend dir to path so `services.xxx` imports work
sys.path.insert(0, os.path.dirname(__file__))

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from database import init_db, USE_POSTGRES, Database
from routers import chat, dimensions
from migrate_111_dimensions import run_migration


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and run migration on startup."""
    try:
        print(f"[Startup] Using database: {'PostgreSQL' if USE_POSTGRES else 'SQLite'}")
        if USE_POSTGRES:
            db_url = os.environ.get('DATABASE_URL', '')
            print(f"[Startup] DATABASE_URL: {db_url[:50] if db_url else 'None'}...")

        # Initialize schema
        await init_db()
        print("[Startup] Schema initialized")

        # Run 111 dimensions migration
        db = Database()
        await db.connect()
        try:
            count = await run_migration(db)
            print(f"[Startup] Migration complete: {count} dimensions")
        except Exception as e:
            print(f"[Startup] Migration error: {e}")
        finally:
            await db.close()

    except Exception as e:
        print(f"[Startup] Error during init: {e}")
        import traceback
        traceback.print_exc()

    yield


app = FastAPI(
    title="提示词工程维度管理平台",
    description="Prompt Engineering Dimension Platform — 111 个维度管理",
    version="2.1.0",
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
    return {
        "status": "ok",
        "service": "prompt-engineering-v2",
        "database": "postgresql" if USE_POSTGRES else "sqlite"
    }


@app.get("/")
async def root():
    return {
        "service": "提示词工程维度管理平台",
        "version": "2.1.0",
        "database": "postgresql" if USE_POSTGRES else "sqlite",
        "endpoints": {
            "/api/health": "Health check",
            "/api/dimensions": "List dimensions",
            "/api/dimensions/categories": "List categories",
            "/docs": "API documentation"
        }
    }


# Static files — MUST be after all API routes
static_dir = "/app/static"
os.makedirs(static_dir, exist_ok=True)
index_path = os.path.join(static_dir, "index.html")

if os.path.exists(index_path):
    # Serve static assets (js, css, images)
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets"), html=True), name="assets")

    # SPA fallback: any non-API path returns index.html
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Skip API routes
        if full_path.startswith("api/"):
            return JSONResponse({"error": "Not found"}, status_code=404)

        # If file exists in static dir, serve it
        file_path = os.path.join(static_dir, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        # Otherwise return index.html for SPA routing
        return FileResponse(index_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
