"""Simple migration script for 111 dimensions."""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from import_111_dimensions import DIMENSION_DATA

# Check if using PostgreSQL
DATABASE_URL = os.environ.get("DATABASE_URL")
USE_POSTGRES = DATABASE_URL and DATABASE_URL.startswith("postgresql")

if __name__ == "__main__":
    print(f"DATABASE_URL: {DATABASE_URL[:40] if DATABASE_URL else 'None'}...")
    print(f"Using PostgreSQL: {USE_POSTGRES}")
    print(f"Total dimensions to import: {len(DIMENSION_DATA)}")

    if USE_POSTGRES:
        import asyncpg

        async def migrate():
            conn = await asyncpg.connect(DATABASE_URL)

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

            # Clear existing data
            await conn.execute("TRUNCATE TABLE dimensions")

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
            print(f"Imported {count} dimensions to PostgreSQL")

            # Show category distribution
            cats = await conn.fetch("""
                SELECT category, category_name, COUNT(*) as count
                FROM dimensions
                GROUP BY category, category_name
                ORDER BY category
            """)
            print("\nCategory distribution:")
            for cat in cats:
                print(f"  {cat['category']} ({cat['category_name']}): {cat['count']}")

            await conn.close()

        asyncio.run(migrate())
    else:
        import sqlite3

        DB_DIR = os.path.join(os.path.dirname(__file__), "data")
        DB_PATH = os.path.join(DB_DIR, "prompt_engineering.db")
        os.makedirs(DB_DIR, exist_ok=True)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Drop and recreate
        cursor.execute("DROP TABLE IF EXISTS dimensions")
        cursor.execute("""
            CREATE TABLE dimensions (
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

        # Insert dimensions
        now = datetime.now().isoformat()
        for dim in DIMENSION_DATA:
            level = dim.get('level')
            cursor.execute("""
                INSERT INTO dimensions
                (id, name, category, category_name, description, data_source, update_frequency, level, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dim['id'], dim['name'], dim['category'], dim['category_name'],
                dim['description'], dim['data_source'], dim['update_frequency'],
                level, now, now
            ))

        conn.commit()

        # Verify
        cursor.execute("SELECT COUNT(*) FROM dimensions")
        count = cursor.fetchone()[0]
        print(f"Imported {count} dimensions to SQLite")

        conn.close()

    print("\nMigration completed!")
