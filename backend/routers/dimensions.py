"""Dimensions CRUD router."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException

from database import Database

router = APIRouter(prefix="/api", tags=["dimensions"])


async def get_db() -> Database:
    """Get database connection."""
    db = Database()
    await db.connect()
    return db


@router.get("/dimensions/categories")
async def get_categories(db: Database = Depends(get_db)):
    """Get all dimension categories with counts."""
    try:
        rows = await db.fetch_all(
            "SELECT category, category_name, COUNT(*) as count FROM dimensions GROUP BY category, category_name ORDER BY category"
        )
        return [
            {"key": row["category"], "name": row["category_name"], "count": row["count"]}
            for row in rows
        ]
    finally:
        await db.close()


@router.get("/dimensions")
async def get_dimensions(
    category: str = None,
    db: Database = Depends(get_db),
):
    """Get dimensions, optionally filtered by category."""
    try:
        if category:
            rows = await db.fetch_all(
                "SELECT * FROM dimensions WHERE category = $1 ORDER BY id, level",
                (category,)
            )
        else:
            rows = await db.fetch_all("SELECT * FROM dimensions ORDER BY id")
        return rows
    finally:
        await db.close()


@router.get("/dimensions/{dimension_id}")
async def get_dimension(
    dimension_id: str,
    db: Database = Depends(get_db),
):
    """Get a single dimension by ID."""
    try:
        row = await db.fetch_one(
            "SELECT * FROM dimensions WHERE id = $1",
            (dimension_id,)
        )
        if not row:
            raise HTTPException(status_code=404, detail="维度不存在")
        return row
    finally:
        await db.close()


@router.put("/dimensions/{dimension_id}")
async def update_dimension(
    dimension_id: str,
    body: Dict[str, Any],
    db: Database = Depends(get_db),
):
    """Update a dimension's fields."""
    try:
        # Check if exists
        existing = await db.fetch_one(
            "SELECT * FROM dimensions WHERE id = $1",
            (dimension_id,)
        )
        if not existing:
            raise HTTPException(status_code=404, detail="维度不存在")

        # Build updates
        updates = {}
        for field in ["name", "category", "category_name", "description",
                      "data_source", "update_frequency", "source_explanation"]:
            val = body.get(field)
            if val is not None:
                updates[field] = val

        if not updates:
            return existing

        updates["updated_at"] = datetime.now().isoformat()
        set_clause = ", ".join(f"{k} = ${i+1}" for i, k in enumerate(updates.keys()))
        values = list(updates.values()) + [dimension_id]

        await db.execute(
            f"UPDATE dimensions SET {set_clause} WHERE id = ${len(values)}",
            values
        )

        return await db.fetch_one(
            "SELECT * FROM dimensions WHERE id = $1",
            (dimension_id,)
        )
    finally:
        await db.close()


@router.delete("/dimensions/{dimension_id}")
async def delete_dimension(
    dimension_id: str,
    db: Database = Depends(get_db),
):
    """Delete a dimension."""
    try:
        existing = await db.fetch_one(
            "SELECT id FROM dimensions WHERE id = $1",
            (dimension_id,)
        )
        if not existing:
            raise HTTPException(status_code=404, detail="维度不存在")

        await db.execute("DELETE FROM dimensions WHERE id = $1", (dimension_id,))
        return {"message": f"维度 {dimension_id} 已删除"}
    finally:
        await db.close()
