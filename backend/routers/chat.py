"""Chat router — proxy to AIhub chatflow with streaming + conversation memory.

NEW FLOW (v2):
1. User sends message
2. Backend calls Dimension Analysis Workflow → gets relevant dimension IDs
3. Backend fetches those dimensions from DB → packs them into the query
4. Backend forwards packed query to AIhub chatflow (streaming)
5. User sees AI designer response — the whole process is invisible to them

The AIhub chatflow maintains conversation context via its own conversation_id.
We store the mapping: our local conversation_id ↔ AIhub conversation_id.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime

import aiosqlite
from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse

from database import db_dependency, get_db
from models import ChatRequest, ConversationCreate, ConversationResponse, MessageResponse
from services.aihub_client import chat_stream, analyze_dimensions_workflow

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


# ── Dimension list cache (regenerated on first use / when stale) ──────

_dimension_list_cache: str | None = None
_dimension_list_ts: float = 0.0


async def _get_dimension_list(db: aiosqlite.Connection) -> str:
    """Get compact dimension list string for the analysis workflow.

    Format:
    [A类] 战略与价值观
      A01 战略核心方向
      A02 战略红线清单
      ...
    """
    global _dimension_list_cache, _dimension_list_ts
    import time
    now = time.time()

    # Cache for 5 minutes
    if _dimension_list_cache and (now - _dimension_list_ts) < 300:
        return _dimension_list_cache

    cursor = await db.execute(
        "SELECT id, name, category, category_name FROM dimensions ORDER BY id"
    )
    rows = await cursor.fetchall()

    lines = []
    current_cat = ""
    for r in rows:
        if r["category"] != current_cat:
            current_cat = r["category"]
            lines.append(f"\n[{r['category']}类] {r['category_name']}")
        lines.append(f"  {r['id']} {r['name']}")

    result = "\n".join(lines).strip()
    _dimension_list_cache = result
    _dimension_list_ts = now
    return result


async def _pack_dimensions(db: aiosqlite.Connection, dimension_ids: list[str]) -> str:
    """Fetch selected dimensions from DB and pack them into a structured string.

    Each dimension is packed as:
    ---
    【维度 A01】战略核心方向
    定义：DJ最近3次会议中强调的战略重点...
    质量作用：战略对齐刚性检查：设计必须对齐至少1个战略重点
    ---
    """
    if not dimension_ids:
        return ""

    placeholders = ",".join("?" for _ in dimension_ids)
    cursor = await db.execute(
        f"SELECT id, name, description, quality_role FROM dimensions WHERE id IN ({placeholders}) ORDER BY id",
        dimension_ids,
    )
    rows = await cursor.fetchall()

    parts = []
    for r in rows:
        block = f"【维度 {r['id']}】{r['name']}"
        if r["description"]:
            block += f"\n定义：{r['description']}"
        if r["quality_role"]:
            block += f"\n质量作用：{r['quality_role']}"
        parts.append(block)

    return "\n---\n".join(parts)


def _build_enhanced_query(user_message: str, packed_dimensions: str) -> str:
    """Combine user message with packed dimension context for the chatflow.

    The user's original message is preserved; dimensions are prepended as context.
    """
    if not packed_dimensions:
        return user_message

    return (
        f"以下是与用户需求相关的维度信息，请基于这些维度为用户提供专业的设计方案：\n\n"
        f"{packed_dimensions}\n\n"
        f"---\n\n"
        f"用户需求：{user_message}"
    )


# ── Routes ────────────────────────────────────────────────────────────


@router.post("/conversations")
async def create_conversation(
    body: ConversationCreate,
    db: aiosqlite.Connection = Depends(db_dependency),
):
    """Create a new conversation."""
    conv_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    await db.execute(
        """INSERT INTO conversations (id, title, aihub_conversation_id, created_at, updated_at)
           VALUES (?, ?, NULL, ?, ?)""",
        (conv_id, body.title or "新对话", now, now),
    )
    await db.commit()
    return ConversationResponse(
        id=conv_id,
        title=body.title or "新对话",
        created_at=now,
        updated_at=now,
    )


@router.get("/chat/{conversation_id}/history")
async def get_history(
    conversation_id: str,
    db: aiosqlite.Connection = Depends(db_dependency),
):
    """Get conversation history with all messages."""
    cursor = await db.execute(
        "SELECT * FROM conversations WHERE id = ?", (conversation_id,)
    )
    conv = await cursor.fetchone()
    if not conv:
        return {"error": "对话不存在", "conversation_id": conversation_id}

    cursor = await db.execute(
        "SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC",
        (conversation_id,),
    )
    rows = await cursor.fetchall()
    messages = []
    for row in rows:
        messages.append(MessageResponse(
            id=row["id"],
            conversation_id=row["conversation_id"],
            role=row["role"],
            content=row["content"],
            created_at=row["created_at"],
        ))

    return {
        "conversation": ConversationResponse(
            id=conv["id"],
            title=conv["title"],
            created_at=conv["created_at"],
            updated_at=conv["updated_at"],
        ),
        "messages": messages,
    }


@router.post("/chat")
async def chat(body: ChatRequest):
    """Stream chat response via SSE, proxying to AIhub chatflow.

    Enhanced Flow (v2):
    1. Save user message to local DB
    2. Call Dimension Analysis Workflow → get relevant dimension IDs
    3. Fetch those dimensions from DB → pack into structured context
    4. Build enhanced query = packed dimensions + user message
    5. Forward enhanced query to AIhub chatflow via streaming
    6. Stream tokens back to frontend via SSE (user sees only the AI response)
    7. Save assistant response to local DB
    8. Store AIhub conversation_id for future rounds
    """

    async def event_generator():
        db = await get_db()
        try:
            now = datetime.now().isoformat()

            # Save user message (original, without dimension packing)
            await db.execute(
                "INSERT INTO messages (conversation_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                (body.conversation_id, "user", body.message, now),
            )
            await db.commit()

            # Get AIhub conversation_id for memory continuity
            cursor = await db.execute(
                "SELECT aihub_conversation_id FROM conversations WHERE id = ?",
                (body.conversation_id,),
            )
            row = await cursor.fetchone()
            aihub_conv_id = row["aihub_conversation_id"] if row else None

            # ── Step 1: Dimension Analysis (only for first message in conversation) ──
            enhanced_query = body.message
            is_first_message = aihub_conv_id is None

            if is_first_message:
                try:
                    # Send a "thinking" event so the frontend knows we're analyzing
                    yield {
                        "data": json.dumps({
                            "type": "status",
                            "content": "正在分析需求，匹配最佳维度...",
                        }, ensure_ascii=False)
                    }

                    # Get dimension list for the analysis workflow
                    dimension_list = await _get_dimension_list(db)

                    # Call analysis workflow
                    logger.info(f"[Chat] Calling dimension analysis workflow for: {body.message[:50]}...")
                    selected_ids = await analyze_dimensions_workflow(
                        user_query=body.message,
                        dimension_list=dimension_list,
                        user=f"chat-analyzer-{body.conversation_id[:8]}",
                    )
                    logger.info(f"[Chat] Analysis returned {len(selected_ids)} dimensions: {selected_ids}")

                    # Pack selected dimensions
                    packed = await _pack_dimensions(db, selected_ids)
                    if packed:
                        enhanced_query = _build_enhanced_query(body.message, packed)
                        logger.info(f"[Chat] Enhanced query length: {len(enhanced_query)} chars ({len(selected_ids)} dimensions)")

                    yield {
                        "data": json.dumps({
                            "type": "status",
                            "content": f"已匹配 {len(selected_ids)} 个维度，正在生成设计方案...",
                        }, ensure_ascii=False)
                    }

                except Exception as e:
                    logger.warning(f"[Chat] Dimension analysis failed, falling back to raw query: {e}")
                    # Fall back to raw user message if analysis fails
                    enhanced_query = body.message
                    yield {
                        "data": json.dumps({
                            "type": "status",
                            "content": "维度分析跳过，直接生成方案...",
                        }, ensure_ascii=False)
                    }

            # ── Step 2: Stream from AIhub chatflow ──
            full_response = ""
            new_aihub_conv_id = None

            async for chunk in chat_stream(
                query=enhanced_query,
                user=f"user-{body.conversation_id[:8]}",
                conversation_id=aihub_conv_id,
            ):
                if chunk["type"] == "metadata":
                    new_aihub_conv_id = chunk.get("conversation_id")
                    yield {
                        "data": json.dumps({
                            "type": "metadata",
                            "conversation_id": body.conversation_id,
                        }, ensure_ascii=False)
                    }

                elif chunk["type"] == "token":
                    full_response += chunk["content"]
                    yield {
                        "data": json.dumps({
                            "type": "token",
                            "content": chunk["content"],
                        }, ensure_ascii=False)
                    }

                elif chunk["type"] == "done":
                    full_response = chunk.get("content", full_response)
                    if not new_aihub_conv_id:
                        new_aihub_conv_id = chunk.get("conversation_id")
                    yield {
                        "data": json.dumps({
                            "type": "done",
                            "content": "",
                        }, ensure_ascii=False)
                    }

                elif chunk["type"] == "error":
                    yield {
                        "data": json.dumps({
                            "type": "error",
                            "content": chunk["content"],
                        }, ensure_ascii=False)
                    }
                    return

            # Save assistant message
            assistant_now = datetime.now().isoformat()
            await db.execute(
                """INSERT INTO messages (conversation_id, role, content, created_at)
                   VALUES (?, ?, ?, ?)""",
                (body.conversation_id, "assistant", full_response, assistant_now),
            )

            # Store AIhub conversation_id for memory continuity
            if new_aihub_conv_id:
                await db.execute(
                    "UPDATE conversations SET aihub_conversation_id = ?, updated_at = ? WHERE id = ?",
                    (new_aihub_conv_id, assistant_now, body.conversation_id),
                )

            # Update conversation title
            cursor = await db.execute(
                "SELECT title FROM conversations WHERE id = ?", (body.conversation_id,)
            )
            conv = await cursor.fetchone()
            if conv and conv["title"] == "新对话":
                title = body.message[:30] + ("..." if len(body.message) > 30 else "")
                await db.execute(
                    "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?",
                    (title, assistant_now, body.conversation_id),
                )
            else:
                await db.execute(
                    "UPDATE conversations SET updated_at = ? WHERE id = ?",
                    (assistant_now, body.conversation_id),
                )
            await db.commit()
        finally:
            await db.close()

    return EventSourceResponse(event_generator())
