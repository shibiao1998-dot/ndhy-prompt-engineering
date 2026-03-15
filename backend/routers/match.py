"""Dimension matching router."""

from __future__ import annotations

import aiosqlite
from fastapi import APIRouter, Depends

from database import db_dependency
from models import MatchRequest, MatchResponse, MatchedDimension
from services.dimension_matcher import match_dimensions

router = APIRouter(prefix="/api/dimensions", tags=["match"])


@router.post("/match")
async def match(
    body: MatchRequest,
    db: aiosqlite.Connection = Depends(db_dependency),
):
    """Match a task description to relevant dimensions using AI."""
    cursor = await db.execute("SELECT * FROM dimensions ORDER BY id")
    rows = await cursor.fetchall()
    all_dims = [dict(row) for row in rows]

    matched = await match_dimensions(body.task_description, all_dims)

    return MatchResponse(
        matched_dimensions=[
            MatchedDimension(
                id=m["id"],
                name=m["name"],
                priority=m["priority"],
                reason=m.get("reason"),
            )
            for m in matched
        ],
        total_matched=len(matched),
    )
