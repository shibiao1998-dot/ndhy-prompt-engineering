"""Simple migration script for 111 dimensions."""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from import_111_dimensions import DIMENSION_DATA

# Check if using PostgreSQL
DATABASE_URL = os.environ.get("DATABASE_URL")
USE_POSTGRES = DATABASE_URL and DATABASE_URL.startswith("postgresql")


async def migrate_postgres(conn):
    """Migrate to PostgreSQL."""
    import asyncpg

    # Create table
    await conn.execute("""
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
        )
    """)

    # Check if data already exists
    result = await conn.fetch("SELECT COUNT(*) as count FROM dimensions")
    existing_count = result[0]['count']

    if existing_count > 0:
        print(f"[Migration] Table already has {existing_count} dimensions, skipping import")
        return existing_count

    # Insert all dimensions
    now = datetime.now().isoformat()
    for dim in DIMENSION_DATA:
        level = dim.get('level')
        await conn.execute("""
            INSERT INTO dimensions
            (id, name, category, category_name, description, data_source, update_frequency, level, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        """,
            dim['id'], dim['name'], dim['category'], dim['category_name'],
            dim['description'], dim['data_source'], dim['update_frequency'],
            level, now, now
        )

    # Verify
    result = await conn.fetch("SELECT COUNT(*) as count FROM dimensions")
    count = result[0]['count']
    return count


async def migrate_sqlite(conn):
    """Migrate to SQLite."""
    import aiosqlite

    db_path = os.path.join(os.path.dirname(conn), "data", "prompt_engineering.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    async with aiosqlite.connect(db_path) as db:
        # Create table
        await db.execute("""
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
            )
        """)

        # Check if data already exists
        cursor = await db.execute("SELECT COUNT(*) FROM dimensions")
        row = await cursor.fetchone()
        existing_count = row[0]

        if existing_count > 0:
            print(f"[Migration] Table already has {existing_count} dimensions, skipping import")
            return existing_count

        # Insert all dimensions
        now = datetime.now().isoformat()
        for dim in DIMENSION_DATA:
            level = dim.get('level')
            await db.execute("""
                INSERT INTO dimensions
                (id, name, category, category_name, description, data_source, update_frequency, level, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dim['id'], dim['name'], dim['category'], dim['category_name'],
                dim['description'], dim['data_source'], dim['update_frequency'],
                level, now, now
            ))

        await db.commit()

        # Verify
        cursor = await db.execute("SELECT COUNT(*) FROM dimensions")
        row = await cursor.fetchone()
        return row[0]


async def run_migration(conn):
    """Run migration based on database type."""
    if USE_POSTGRES:
        count = await migrate_postgres(conn)
        print(f"[Migration] PostgreSQL: {count} dimensions imported")
    else:
        count = await migrate_sqlite(conn)
        print(f"[Migration] SQLite: {count} dimensions imported")

    return count
