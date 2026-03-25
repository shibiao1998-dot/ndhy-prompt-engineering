"""Database initialization and connection management.

Supports both SQLite (local) and PostgreSQL (Railway).
Uses PostgreSQL when DATABASE_URL env var is set (Railway auto-injects this).
"""

import os
import aiosqlite

# Check if using PostgreSQL (Railway provides DATABASE_URL)
DATABASE_URL = os.environ.get("DATABASE_URL")
USE_POSTGRES = DATABASE_URL and DATABASE_URL.startswith("postgresql")

if USE_POSTGRES:
    import asyncpg
    DB_PATH = DATABASE_URL
else:
    DB_DIR = os.path.join(os.path.dirname(__file__), "data")
    DB_PATH = os.path.join(DB_DIR, "prompt_engineering.db")

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


async def get_db():
    """Get a database connection."""
    if USE_POSTGRES:
        db = await asyncpg.connect(DATABASE_URL)
        return PostgresWrapper(db)
    else:
        os.makedirs(DB_DIR, exist_ok=True)
        db = await aiosqlite.connect(DB_PATH)
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("PRAGMA foreign_keys=OFF")
        return SQLiteWrapper(db)


class PostgresWrapper:
    """Wrapper to make asyncpg behave like aiosqlite for our use case."""

    def __init__(self, conn):
        self._conn = conn

    async def execute(self, query, params=None):
        if params:
            result = await self._conn.fetch(query, *params)
        else:
            result = await self._conn.fetch(query)
        return CursorResult(result)

    async def executemany(self, query, params_list):
        for params in params_list:
            await self._conn.execute(query, *params)

    async def commit(self):
        pass  # asyncpg auto-commits

    async def close(self):
        await self._conn.close()


class CursorResult:
    """Wrapper to make asyncpg result behave like aiosqlite cursor."""

    def __init__(self, rows):
        self._rows = rows
        self._index = 0

    async def fetchall(self):
        return self._rows

    async def fetchone(self):
        if self._index < len(self._rows):
            row = self._rows[self._index]
            self._index += 1
            return RowWrapper(row)
        return None


class RowWrapper:
    """Wrapper to make asyncpg Row behave like aiosqlite Row."""

    def __init__(self, row):
        self._row = row

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._row[key]
        return self._row[key]

    def get(self, key, default=None):
        try:
            return self._row[key]
        except (KeyError, IndexError):
            return default


class SQLiteWrapper:
    """Wrapper for aiosqlite connection."""

    def __init__(self, conn):
        self._conn = conn

    async def execute(self, query, params=None):
        if params:
            return await self._conn.execute(query, params)
        return await self._conn.execute(query)

    async def executemany(self, query, params_list):
        return await self._conn.executemany(query, params_list)

    async def commit(self):
        await self._conn.commit()

    async def close(self):
        await self._conn.close()


async def init_db():
    """Initialize database tables."""
    db = await get_db()
    try:
        if USE_POSTGRES:
            # PostgreSQL uses different syntax
            await db.execute(SCHEMA, None)
        else:
            await db.execute(SCHEMA)
            await db.commit()
    finally:
        await db.close()


async def db_dependency():
    """FastAPI dependency that yields a database connection."""
    db = await get_db()
    try:
        yield db
    finally:
        await db.close()
