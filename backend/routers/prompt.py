"""Prompt preview and engine adaptation router."""

from __future__ import annotations

import aiosqlite
from fastapi import APIRouter, Depends

from database import db_dependency
from models import (
    PromptAdaptRequest,
    PromptAdaptResponse,
    PromptPreviewRequest,
    PromptPreviewResponse,
)
from services.engine_adapter import adapt_prompt
from services.prompt_assembler import assemble_system_prompt

router = APIRouter(prefix="/api/prompt", tags=["prompt"])


@router.post("/preview")
async def preview_prompt(
    body: PromptPreviewRequest,
    db: aiosqlite.Connection = Depends(db_dependency),
):
    """Preview the assembled system prompt for given dimensions."""
    if not body.dimension_ids:
        return {"error": "请提供至少一个维度 ID"}

    placeholders = ",".join("?" for _ in body.dimension_ids)
    cursor = await db.execute(
        f"SELECT * FROM dimensions WHERE id IN ({placeholders})",
        body.dimension_ids,
    )
    rows = await cursor.fetchall()
    dim_list = [dict(row) for row in rows]

    result = assemble_system_prompt(
        dimensions=dim_list,
        task_description=body.task_description,
    )

    return PromptPreviewResponse(
        system_prompt=result["system_prompt"],
        positive_section=result["positive_section"],
        constraint_section=result["constraint_section"],
        dimensions_used=result["dimensions_used"],
        coverage_stats=result["coverage_stats"],
    )


@router.post("/adapt")
async def adapt(body: PromptAdaptRequest):
    """Adapt a prompt to a specific engine format."""
    result = adapt_prompt(body.prompt_text, body.engine_id)
    return PromptAdaptResponse(**result)
