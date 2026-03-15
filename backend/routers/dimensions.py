"""Dimensions CRUD router."""

from __future__ import annotations

from datetime import datetime

import aiosqlite
from fastapi import APIRouter, Depends, Query

from database import db_dependency
from models import DimensionCreate, DimensionResponse, DimensionUpdate

router = APIRouter(prefix="/api/dimensions", tags=["dimensions"])


def _row_to_response(row) -> DimensionResponse:
    return DimensionResponse(
        id=row["id"],
        name=row["name"],
        category=row["category"],
        category_name=row["category_name"],
        description=row["description"],
        pending_description=row["pending_description"],
        data_source=row["data_source"],
        update_frequency=row["update_frequency"],
        direction=row["direction"] or "positive",
        priority=row["priority"] or 2,
        last_updated_at=row["last_updated_at"],
        review_status=row["review_status"] or "approved",
        reviewer=row["reviewer"],
        reviewed_at=row["reviewed_at"],
        created_at=row["created_at"],
    )


@router.get("")
async def list_dimensions(
    category: str | None = Query(None, description="Filter by category (e.g., A, B, C)"),
    db: aiosqlite.Connection = Depends(db_dependency),
):
    """Get all dimensions, optionally filtered by category."""
    if category:
        cursor = await db.execute(
            "SELECT * FROM dimensions WHERE category = ? ORDER BY id", (category,)
        )
    else:
        cursor = await db.execute("SELECT * FROM dimensions ORDER BY id")
    rows = await cursor.fetchall()
    return [_row_to_response(row) for row in rows]


@router.get("/{dimension_id}")
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
        return {"error": f"维度 {dimension_id} 不存在"}
    return _row_to_response(row)


@router.post("")
async def create_dimension(
    body: DimensionCreate,
    db: aiosqlite.Connection = Depends(db_dependency),
):
    """Create a new dimension."""
    now = datetime.now().isoformat()
    await db.execute(
        """INSERT INTO dimensions
           (id, name, category, category_name, description, data_source,
            update_frequency, direction, priority, created_at, last_updated_at, review_status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'approved')""",
        (body.id, body.name, body.category, body.category_name,
         body.description, body.data_source, body.update_frequency,
         body.direction, body.priority, now, now),
    )
    await db.commit()
    return {"message": f"维度 {body.id} 创建成功", "id": body.id}


@router.put("/{dimension_id}")
async def update_dimension(
    dimension_id: str,
    body: DimensionUpdate,
    db: aiosqlite.Connection = Depends(db_dependency),
):
    """Update a dimension. Description changes go to pending_description."""
    cursor = await db.execute(
        "SELECT * FROM dimensions WHERE id = ?", (dimension_id,)
    )
    row = await cursor.fetchone()
    if not row:
        return {"error": f"维度 {dimension_id} 不存在"}

    now = datetime.now().isoformat()
    updates = []
    params = []

    # Description changes go to pending_description
    if body.description is not None:
        updates.append("pending_description = ?")
        params.append(body.description)
        updates.append("review_status = ?")
        params.append("pending")

    # Other fields update directly
    if body.name is not None:
        updates.append("name = ?")
        params.append(body.name)
    if body.category is not None:
        updates.append("category = ?")
        params.append(body.category)
    if body.category_name is not None:
        updates.append("category_name = ?")
        params.append(body.category_name)
    if body.data_source is not None:
        updates.append("data_source = ?")
        params.append(body.data_source)
    if body.update_frequency is not None:
        updates.append("update_frequency = ?")
        params.append(body.update_frequency)
    if body.direction is not None:
        updates.append("direction = ?")
        params.append(body.direction)
    if body.priority is not None:
        updates.append("priority = ?")
        params.append(body.priority)

    updates.append("last_updated_at = ?")
    params.append(now)
    params.append(dimension_id)

    if updates:
        sql = f"UPDATE dimensions SET {', '.join(updates)} WHERE id = ?"
        await db.execute(sql, params)
        await db.commit()

    return {"message": f"维度 {dimension_id} 更新成功", "review_status": "pending" if body.description else "unchanged"}


@router.delete("/{dimension_id}")
async def delete_dimension(
    dimension_id: str,
    db: aiosqlite.Connection = Depends(db_dependency),
):
    """Delete a dimension."""
    cursor = await db.execute(
        "SELECT id FROM dimensions WHERE id = ?", (dimension_id,)
    )
    row = await cursor.fetchone()
    if not row:
        return {"error": f"维度 {dimension_id} 不存在"}

    await db.execute("DELETE FROM dimensions WHERE id = ?", (dimension_id,))
    await db.commit()
    return {"message": f"维度 {dimension_id} 已删除"}
