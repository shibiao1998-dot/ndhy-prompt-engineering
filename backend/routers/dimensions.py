"""Dimensions CRUD router — manage 11 categories and 111 dimensions."""

from __future__ import annotations

from datetime import datetime

import aiosqlite
from fastapi import APIRouter, Depends, HTTPException

from database import db_dependency
from models import DimensionResponse, DimensionUpdate

router = APIRouter(prefix="/api", tags=["dimensions"])


@router.get("/dimensions/categories")
async def get_categories(db: aiosqlite.Connection = Depends(db_dependency)):
    """Get all dimension categories with counts."""
    cursor = await db.execute(
        """SELECT category, category_name, COUNT(*) as count
           FROM dimensions GROUP BY category ORDER BY category"""
    )
    rows = await cursor.fetchall()
    return [
        {"key": row["category"], "name": row["category_name"], "count": row["count"]}
        for row in rows
    ]


@router.get("/dimensions")
async def get_dimensions(
    category: str | None = None,
    db: aiosqlite.Connection = Depends(db_dependency),
):
    """Get dimensions, optionally filtered by category."""
    if category:
        cursor = await db.execute(
            "SELECT * FROM dimensions WHERE category = ? ORDER BY id, level",
            (category,),
        )
    else:
        cursor = await db.execute("SELECT * FROM dimensions ORDER BY id")
    rows = await cursor.fetchall()
    return [_row_to_dict(row) for row in rows]


@router.get("/dimensions/{dimension_id}")
async def get_dimension(
    dimension_id: str,
    db: aiosqlite.Connection = Depends(db_dependency),
):
    """Get a single dimension by ID."""
    cursor = await db.execute(
        "SELECT * FROM dimensions WHERE id = ?", (dimension_id,)
    )
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="维度不存在")
    return _row_to_dict(row)


@router.put("/dimensions/{dimension_id}")
async def update_dimension(
    dimension_id: str,
    body: DimensionUpdate,
    db: aiosqlite.Connection = Depends(db_dependency),
):
    """Update a dimension's fields."""
    cursor = await db.execute(
        "SELECT * FROM dimensions WHERE id = ?", (dimension_id,)
    )
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="维度不存在")

    updates = {}
    for field in ["name", "category", "category_name", "description",
                   "data_source", "update_frequency",
                   "source_explanation"]:
        val = getattr(body, field, None)
        if val is not None:
            updates[field] = val

    if not updates:
        return _row_to_dict(row)

    updates["updated_at"] = datetime.now().isoformat()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [dimension_id]

    await db.execute(
        f"UPDATE dimensions SET {set_clause} WHERE id = ?",
        values,
    )
    await db.commit()

    cursor = await db.execute(
        "SELECT * FROM dimensions WHERE id = ?", (dimension_id,)
    )
    return _row_to_dict(await cursor.fetchone())


@router.delete("/dimensions/{dimension_id}")
async def delete_dimension(
    dimension_id: str,
    db: aiosqlite.Connection = Depends(db_dependency),
):
    """Delete a dimension."""
    cursor = await db.execute(
        "SELECT id FROM dimensions WHERE id = ?", (dimension_id,)
    )
    if not await cursor.fetchone():
        raise HTTPException(status_code=404, detail="维度不存在")

    await db.execute("DELETE FROM dimensions WHERE id = ?", (dimension_id,))
    await db.commit()
    return {"message": f"维度 {dimension_id} 已删除"}


def _row_to_dict(row: aiosqlite.Row) -> dict:
    """Convert a database row to a dict for JSON response."""
    return {
        "id": row["id"],
        "name": row["name"],
        "category": row["category"],
        "category_name": row["category_name"],
        "description": row["description"],
        "data_source": row["data_source"],
        "update_frequency": row["update_frequency"],
        "source_explanation": row["source_explanation"],
        "level": row["level"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }
