"""Database initialization and connection management.

Supports both SQLite (local) and PostgreSQL (Railway).
Uses PostgreSQL when DATABASE_URL env var is set (Railway auto-injects this).
"""

import os

# Check if using PostgreSQL (Railway provides DATABASE_URL)
DATABASE_URL = os.environ.get("DATABASE_URL")
USE_POSTGRES = DATABASE_URL and DATABASE_URL.startswith("postgresql")

if USE_POSTGRES:
    import asyncpg
else:
    import aiosqlite

SCHEMA = """
-- 维度表
CREATE TABLE IF NOT EXISTS dimensions (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  category_name TEXT,
  description TEXT,
  data_source TEXT,
  update_frequency TEXT,
  source_explanation TEXT,
  level INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 对话表
CREATE TABLE IF NOT EXISTS conversations (
  id TEXT PRIMARY KEY,
  title TEXT,
  task_type TEXT,
  aihub_conversation_id TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 消息表
CREATE TABLE IF NOT EXISTS messages (
  id SERIAL PRIMARY KEY,
  conversation_id TEXT REFERENCES conversations(id),
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  dimensions_used TEXT,
  prompt_snapshot TEXT,
  coverage_stats TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 维度审核日志
CREATE TABLE IF NOT EXISTS dimension_reviews (
  id SERIAL PRIMARY KEY,
  dimension_id TEXT REFERENCES dimensions(id),
  old_description TEXT,
  new_description TEXT,
  action TEXT NOT NULL,
  reviewer TEXT,
  comment TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


class Database:
    """Database connection manager."""

    def __init__(self):
        self._conn = None

    async def connect(self):
        if USE_POSTGRES:
            self._conn = await asyncpg.connect(DATABASE_URL)
        else:
            db_path = os.path.join(os.path.dirname(__file__), "data", "prompt_engineering.db")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            self._conn = await aiosqlite.connect(db_path)
            await self._conn.execute("PRAGMA journal_mode=WAL")
            await self._conn.execute("PRAGMA foreign_keys=OFF")
        return self

    async def close(self):
        if self._conn:
            await self._conn.close()

    async def execute(self, query, params=None):
        if USE_POSTGRES:
            if params:
                return await self._conn.execute(query, *params)
            return await self._conn.execute(query)
        else:
            if params:
                return await self._conn.execute(query, params)
            return await self._conn.execute(query)

    async def fetch_all(self, query, params=None):
        if USE_POSTGRES:
            if params:
                return await self._conn.fetch(query, *params)
            return await self._conn.fetch(query)
        else:
            async with aiosqlite.connect(
                os.path.join(os.path.dirname(__file__), "data", "prompt_engineering.db")
            ) as db:
                await db.execute("PRAGMA journal_mode=WAL")
                if params:
                    cursor = await db.execute(query, params)
                else:
                    cursor = await db.execute(query)
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def fetch_one(self, query, params=None):
        if USE_POSTGRES:
            if params:
                result = await self._conn.fetchrow(query, *params)
            else:
                result = await self._conn.fetchrow(query)
            return dict(result) if result else None
        else:
            async with aiosqlite.connect(
                os.path.join(os.path.dirname(__file__), "data", "prompt_engineering.db")
            ) as db:
                await db.execute("PRAGMA journal_mode=WAL")
                db.row_factory = aiosqlite.Row
                if params:
                    cursor = await db.execute(query, params)
                else:
                    cursor = await db.execute(query)
                row = await cursor.fetchone()
                return dict(row) if row else None


async def get_db():
    """Get a database connection."""
    db = Database()
    await db.connect()
    return db


async def init_db():
    """Initialize database tables."""
    db = await get_db()
    try:
        await db.execute(SCHEMA)
        print("[DB] Schema initialized")
    finally:
        await db.close()


async def db_dependency():
    """FastAPI dependency that yields a database connection."""
    db = await get_db()
    try:
        yield db
    finally:
        await db.close()
