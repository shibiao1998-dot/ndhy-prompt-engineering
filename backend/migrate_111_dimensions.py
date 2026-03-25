"""Simple migration script for 111 dimensions."""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from import_111_dimensions import DIMENSION_DATA


async def run_migration(conn):
    """Run migration - creates table and imports 111 dimensions."""

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
    print("[Migration] Table created")

    # Check if data already exists
    result = await conn.fetch("SELECT COUNT(*) as count FROM dimensions")
    existing_count = result[0]['count']
    print(f"[Migration] Existing count: {existing_count}")

    if existing_count >= 100:
        print(f"[Migration] Table already has {existing_count} dimensions, skipping import")
        return existing_count

    # Insert all dimensions using copy for efficiency
    now = datetime.now().isoformat()

    # Prepare batch insert
    records = []
    for dim in DIMENSION_DATA:
        level = dim.get('level')
        records.append((
            dim['id'], dim['name'], dim['category'], dim['category_name'],
            dim['description'], dim['data_source'], dim['update_frequency'],
            level, now, now
        ))

    # Batch insert
    await conn.copy_records_to_table(
        'dimensions',
        records=records,
        columns=['id', 'name', 'category', 'category_name', 'description',
                 'data_source', 'update_frequency', 'level', 'created_at', 'updated_at']
    )

    print(f"[Migration] Inserted {len(records)} dimensions")

    # Verify
    result = await conn.fetch("SELECT COUNT(*) as count FROM dimensions")
    count = result[0]['count']
    print(f"[Migration] PostgreSQL: {count} dimensions imported")

    return count
