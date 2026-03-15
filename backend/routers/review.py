"""Review router — dimension review (approve/reject)."""

from __future__ import annotations

from datetime import datetime

import aiosqlite
from fastapi import APIRouter, Depends

from database import db_dependency
from models import ReviewRequest, ReviewResponse

router = APIRouter(prefix="/api/dimensions", tags=["review"])


@router.post("/{dimension_id}/review")
async def review_dimension(
    dimension_id: str,
    body: ReviewRequest,
    db: aiosqlite.Connection = Depends(db_dependency),
):
    """Approve or reject a dimension's pending description."""
    cursor = await db.execute(
        "SELECT * FROM dimensions WHERE id = ?", (dimension_id,)
    )
    row = await cursor.fetchone()
    if not row:
        return {"error": f"维度 {dimension_id} 不存在"}

    now = datetime.now().isoformat()
    old_description = row["description"]
    pending = row["pending_description"]

    if body.action == "approve":
        if not pending:
            return {"error": "没有待审核的描述变更"}

        # Log the review
        await db.execute(
            """INSERT INTO dimension_reviews
               (dimension_id, old_description, new_description, action, reviewer, comment, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (dimension_id, old_description, pending, "approve", body.reviewer, body.comment, now),
        )

        # Apply: pending_description → description
        await db.execute(
            """UPDATE dimensions
               SET description = pending_description,
                   pending_description = NULL,
                   review_status = 'approved',
                   reviewer = ?,
                   reviewed_at = ?,
                   last_updated_at = ?
               WHERE id = ?""",
            (body.reviewer, now, now, dimension_id),
        )
        await db.commit()

        return ReviewResponse(
            dimension_id=dimension_id,
            action="approve",
            review_status="approved",
            message=f"维度 {dimension_id} 审核通过，新描述已生效",
        )

    elif body.action == "reject":
        # Log the review
        await db.execute(
            """INSERT INTO dimension_reviews
               (dimension_id, old_description, new_description, action, reviewer, comment, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (dimension_id, old_description, pending, "reject", body.reviewer, body.comment, now),
        )

        # Reject: clear pending, revert status
        await db.execute(
            """UPDATE dimensions
               SET pending_description = NULL,
                   review_status = 'rejected',
                   reviewer = ?,
                   reviewed_at = ?,
                   last_updated_at = ?
               WHERE id = ?""",
            (body.reviewer, now, now, dimension_id),
        )
        await db.commit()

        return ReviewResponse(
            dimension_id=dimension_id,
            action="reject",
            review_status="rejected",
            message=f"维度 {dimension_id} 审核被驳回",
        )

    else:
        return {"error": f"无效的审核操作: {body.action}，支持 approve/reject"}
