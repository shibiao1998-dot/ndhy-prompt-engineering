"""SQLite database initialization and connection management using aiosqlite."""

import os
import aiosqlite

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
  pending_description TEXT,
  data_source TEXT,
  update_frequency TEXT,
  direction TEXT DEFAULT 'positive',
  priority INTEGER DEFAULT 2,
  last_updated_at TIMESTAMP,
  review_status TEXT DEFAULT 'approved',
  reviewer TEXT,
  reviewed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 对话表
CREATE TABLE IF NOT EXISTS conversations (
  id TEXT PRIMARY KEY,
  title TEXT,
  task_type TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 消息表
CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
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
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  dimension_id TEXT REFERENCES dimensions(id),
  old_description TEXT,
  new_description TEXT,
  action TEXT NOT NULL,
  reviewer TEXT,
  comment TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


async def get_db() -> aiosqlite.Connection:
    """Get a database connection. Caller is responsible for closing it."""
    os.makedirs(DB_DIR, exist_ok=True)
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def init_db():
    """Initialize database tables."""
    db = await get_db()
    try:
        await db.executescript(SCHEMA)
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
