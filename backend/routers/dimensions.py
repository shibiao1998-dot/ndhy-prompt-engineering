"""Dimensions CRUD router — manage 12 categories and 99 dimensions."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime

import aiosqlite
from fastapi import APIRouter, Depends, HTTPException

from database import db_dependency
from models import DimensionResponse, DimensionUpdate, WorkflowRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["dimensions"])

# ── Workflow concurrency limiter: max 5 simultaneous updates ──
_workflow_semaphore = asyncio.Semaphore(5)
_workflow_active_count = 0  # for status reporting


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
            "SELECT * FROM dimensions WHERE category = ? ORDER BY id",
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
                   "quality_role", "data_source", "update_frequency",
                   "source_explanation"]:
        val = getattr(body, field, None)
        if val is not None:
            updates[field] = val

    # Legacy compatibility: raw_content maps to quality_role
    if body.raw_content is not None and "quality_role" not in updates:
        updates["quality_role"] = body.raw_content

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


@router.get("/dimensions/workflow-status")
async def workflow_status():
    """Return current workflow concurrency status."""
    return {
        "active": _workflow_active_count,
        "max": 5,
        "available": 5 - _workflow_active_count,
    }


@router.post("/dimensions/{dimension_id}/update-via-workflow")
async def update_via_workflow(
    dimension_id: str,
    body: WorkflowRequest,
    db: aiosqlite.Connection = Depends(db_dependency),
):
    """Trigger AIhub workflow to update a dimension's definition and data source.

    Concurrency limited to 5 simultaneous workflow calls.

    1. Sends dimension_input to the workflow
    2. Gets back dimension_definition and source_explanation
    3. Updates database: definition → description, source_explanation → source_explanation
    4. Summarizes source_explanation into short keywords for data_source
    """
    global _workflow_active_count

    from services.aihub_client import workflow_blocking

    cursor = await db.execute(
        "SELECT * FROM dimensions WHERE id = ?", (dimension_id,)
    )
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="维度不存在")

    # Check if semaphore would block (non-blocking check for user feedback)
    if _workflow_active_count >= 5:
        raise HTTPException(
            status_code=429,
            detail=f"更新队列已满（{_workflow_active_count}/5），请等待其他更新完成后再试"
        )

    # Acquire semaphore with concurrency tracking
    async with _workflow_semaphore:
        _workflow_active_count += 1
        logger.info(f"[Workflow] Starting update for {dimension_id} ({_workflow_active_count}/5 active)")
        try:
            result = await workflow_blocking(
                dimension_input=body.dimension_input,
                user=f"dimension-updater-{dimension_id}",
            )
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Workflow 调用失败: {str(e)}")
        finally:
            _workflow_active_count -= 1
            logger.info(f"[Workflow] Finished update for {dimension_id} ({_workflow_active_count}/5 active)")

    dimension_definition = result.get("dimension_definition", "")
    source_explanation = result.get("source_explanation", "")

    if not dimension_definition and not source_explanation:
        raise HTTPException(
            status_code=502,
            detail=f"Workflow 返回为空，原始响应: {str(result)[:500]}"
        )

    # Summarize source_explanation into short keywords for data_source card display
    data_source_summary = _summarize_source(source_explanation)

    # Update database
    now = datetime.now().isoformat()
    updates = {"updated_at": now}
    if dimension_definition:
        updates["description"] = dimension_definition
    if source_explanation:
        updates["source_explanation"] = source_explanation
    if data_source_summary:
        updates["data_source"] = data_source_summary

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [dimension_id]
    await db.execute(f"UPDATE dimensions SET {set_clause} WHERE id = ?", values)
    await db.commit()

    # Return updated dimension
    cursor = await db.execute("SELECT * FROM dimensions WHERE id = ?", (dimension_id,))
    updated_row = await cursor.fetchone()
    return _row_to_dict(updated_row)


def _summarize_source(source_text: str) -> str:
    """Extract short source keywords from source_explanation.

    Looks for common patterns like 来源/数据/文献/平台/系统/记录/调研/分析
    and returns a concise summary similar to the original data_source format.
    """
    if not source_text or len(source_text) < 10:
        return source_text

    # Common source keywords to extract
    keywords = []
    source_terms = [
        "会议纪要", "用户调研", "数据分析", "竞品分析", "项目复盘",
        "设计方法论平台", "用户访谈", "应用市场", "客服记录", "数据平台",
        "教育文献", "心理学文献", "官方文档", "项目文档", "设计系统",
        "平台规范", "审核记录", "行业报告", "用户反馈", "专家建议",
        "课程标准", "教材", "实验记录", "市场调研", "技术文档",
        "项目管理", "质量管理", "法务", "供应商", "埋点系统",
        "公司文档", "团队沉淀", "需求管理", "失败案例", "历史决策",
        "事务定义", "验证方法", "创新方法论", "决策方法论",
        "社交媒体", "问卷调查", "设备数据", "网络分析",
        "学习目标库", "教育部门", "研究成果", "行业调研",
    ]

    for term in source_terms:
        if term in source_text:
            keywords.append(term)
        if len(keywords) >= 4:
            break

    if keywords:
        return "、".join(keywords)

    # Fallback: take first 60 chars
    return source_text[:60].rstrip("，。、；") + "..."


def _row_to_dict(row: aiosqlite.Row) -> dict:
    """Convert a database row to a dict for JSON response."""
    return {
        "id": row["id"],
        "name": row["name"],
        "category": row["category"],
        "category_name": row["category_name"],
        "description": row["description"],
        "quality_role": row["quality_role"],
        "data_source": row["data_source"],
        "update_frequency": row["update_frequency"],
        "source_explanation": row["source_explanation"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }
