"""Simple migration script for 111 dimensions."""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from import_111_dimensions import DIMENSION_DATA


async def run_migration(db):
    """Run migration - creates table and imports 111 dimensions."""

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
    print("[Migration] Table created")

    # Check if data already exists
    result = await db.fetch_all("SELECT COUNT(*) as cnt FROM dimensions")
    existing_count = result[0]['cnt'] if result else 0
    print(f"[Migration] Existing count: {existing_count}")

    if existing_count >= 100:
        print(f"[Migration] Table already has {existing_count} dimensions, skipping import")
        return existing_count

    # Insert all dimensions - use datetime objects for PostgreSQL
    now = datetime.now()

    for dim in DIMENSION_DATA:
        level = dim.get('level')
        await db.execute("""
            INSERT INTO dimensions (id, name, category, category_name, description,
                                    data_source, update_frequency, level, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            ON CONFLICT (id) DO NOTHING
        """, (
            dim['id'], dim['name'], dim['category'], dim['category_name'],
            dim['description'], dim['data_source'], dim['update_frequency'],
            level, now, now
        ))

    print(f"[Migration] Inserted {len(DIMENSION_DATA)} dimensions")

    # Verify
    result = await db.fetch_all("SELECT COUNT(*) as cnt FROM dimensions")
    count = result[0]['cnt'] if result else 0
    print(f"[Migration] Total: {count} dimensions imported")

    return count
