"""Migrate database to 111 dimensions schema and import new data.

This script:
1. Backs up the existing database
2. Drops and recreates the dimensions table with new schema (no quality_role, adds level)
3. Imports all 111 dimensions from import_111_dimensions.py
4. Preserves other tables (conversations, messages, dimension_reviews)
"""

import os
import shutil
import sqlite3
from datetime import datetime

from import_111_dimensions import DIMENSION_DATA

DB_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DB_DIR, "prompt_engineering.db")


def backup_database():
    """Create a backup of the existing database."""
    if not os.path.exists(DB_PATH):
        print("No existing database to backup.")
        return None

    backup_path = DB_PATH + f".backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(DB_PATH, backup_path)
    print(f"Database backed up to: {backup_path}")
    return backup_path


def migrate_schema(conn: sqlite3.Connection):
    """Migrate the database schema."""
    cursor = conn.cursor()

    # Drop old dimensions table and recreate with new schema
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

    conn.commit()
    print("Schema migration completed.")


def import_dimensions(conn: sqlite3.Connection):
    """Import all 111 dimensions."""
    cursor = conn.cursor()

    now = datetime.now().isoformat()
    inserted = 0

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
        inserted += 1

    conn.commit()
    print(f"Imported {inserted} dimensions.")


def verify_migration(conn: sqlite3.Connection):
    """Verify the migration was successful."""
    cursor = conn.cursor()

    # Count total dimensions
    cursor.execute("SELECT COUNT(*) FROM dimensions")
    total = cursor.fetchone()[0]
    print(f"Total dimensions: {total}")

    # Count by category
    cursor.execute("SELECT category, category_name, COUNT(*) as count FROM dimensions GROUP BY category ORDER BY category")
    rows = cursor.fetchall()
    print("\nCategory distribution:")
    for row in rows:
        print(f"  {row[0]} ({row[1]}): {row[2]}")

    # Verify M class levels
    cursor.execute("SELECT level, COUNT(*) as count FROM dimensions WHERE category = 'M' GROUP BY level ORDER BY level")
    rows = cursor.fetchall()
    print("\nM class level distribution:")
    for row in rows:
        print(f"  Level {row[0]}: {row[1]}")

    # Verify no quality_role column exists
    cursor.execute("PRAGMA table_info(dimensions)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"\nColumns in dimensions table: {columns}")
    assert 'quality_role' not in columns, "quality_role column should not exist"
    assert 'level' in columns, "level column should exist"

    print("\nVerification passed!")


def main():
    """Run the full migration."""
    print("=" * 60)
    print("Starting 111 Dimensions Migration")
    print("=" * 60)

    # Backup
    backup_path = backup_database()

    # Connect and migrate
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    try:
        # Migrate schema
        migrate_schema(conn)

        # Import dimensions
        import_dimensions(conn)

        # Verify
        verify_migration(conn)

        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\nMigration failed: {e}")
        if backup_path:
            print(f"Restoring from backup...")
            shutil.copy2(backup_path, DB_PATH)
            print("Database restored.")
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    main()
