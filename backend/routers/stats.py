"""Dimension statistics router."""

from __future__ import annotations

import aiosqlite
from fastapi import APIRouter, Depends

from database import db_dependency
from models import CategoryStat, DimensionStats

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/dimensions")
async def dimension_stats(
    db: aiosqlite.Connection = Depends(db_dependency),
):
    """Return dimension panoramic statistics."""
    cursor = await db.execute("SELECT * FROM dimensions ORDER BY id")
    rows = await cursor.fetchall()

    total = len(rows)
    filled = sum(1 for r in rows if r["description"] and r["description"].strip())

    # Group by category
    category_map: dict[str, dict] = {}
    for row in rows:
        cat = row["category"]
        if cat not in category_map:
            category_map[cat] = {
                "category": cat,
                "category_name": row["category_name"],
                "total": 0,
                "filled": 0,
            }
        category_map[cat]["total"] += 1
        if row["description"] and row["description"].strip():
            category_map[cat]["filled"] += 1

    categories = []
    for cat_data in sorted(category_map.values(), key=lambda x: x["category"]):
        cat_total = cat_data["total"]
        cat_filled = cat_data["filled"]
        categories.append(CategoryStat(
            category=cat_data["category"],
            category_name=cat_data["category_name"],
            total=cat_total,
            filled=cat_filled,
            fill_rate=round(cat_filled / cat_total, 4) if cat_total else 0,
        ))

    return DimensionStats(
        total_dimensions=total,
        total_categories=len(category_map),
        filled_dimensions=filled,
        unfilled_dimensions=total - filled,
        overall_fill_rate=round(filled / total, 4) if total else 0,
        by_category=categories,
    )
