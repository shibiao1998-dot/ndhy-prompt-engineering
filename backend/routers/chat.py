"""Chat router — SSE streaming, conversation management, history."""

from __future__ import annotations

import json
import uuid
from datetime import datetime

import aiosqlite
from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse

from database import db_dependency, get_db
from models import ChatRequest, ConversationCreate, ConversationResponse, MessageResponse
from services.ai_service import chat_stream
from services.prompt_assembler import assemble_system_prompt

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/conversations")
async def create_conversation(
    body: ConversationCreate,
    db: aiosqlite.Connection = Depends(db_dependency),
):
    """Create a new conversation."""
    conv_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    await db.execute(
        "INSERT INTO conversations (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
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
    # Get conversation
    cursor = await db.execute(
        "SELECT * FROM conversations WHERE id = ?", (conversation_id,)
    )
    conv = await cursor.fetchone()
    if not conv:
        return {"error": "对话不存在", "conversation_id": conversation_id}

    # Get messages
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
            dimensions_used=row["dimensions_used"],
            prompt_snapshot=row["prompt_snapshot"],
            coverage_stats=row["coverage_stats"],
            created_at=row["created_at"],
        ))

    return {
        "conversation": ConversationResponse(
            id=conv["id"],
            title=conv["title"],
            task_type=conv["task_type"],
            created_at=conv["created_at"],
            updated_at=conv["updated_at"],
        ),
        "messages": messages,
    }


@router.post("/chat")
async def chat(body: ChatRequest):
    """Stream chat response via SSE.

    Note: We manage the DB connection inside the generator because
    FastAPI dependency injection closes connections before the SSE
    stream completes.
    """

    async def event_generator():
        db = await get_db()
        try:
            now = datetime.now().isoformat()

            # Save user message
            await db.execute(
                "INSERT INTO messages (conversation_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                (body.conversation_id, "user", body.message, now),
            )
            await db.commit()

            # Get conversation history
            cursor = await db.execute(
                "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY created_at ASC",
                (body.conversation_id,),
            )
            history_rows = await cursor.fetchall()
            messages = [{"role": row["role"], "content": row["content"]} for row in history_rows]

            # Get all approved dimensions for prompt assembly
            cursor = await db.execute(
                "SELECT * FROM dimensions WHERE review_status = 'approved' AND description IS NOT NULL AND description != ''"
            )
            dims = await cursor.fetchall()
            dim_list = [dict(d) for d in dims]

            # Assemble system prompt
            result = assemble_system_prompt(
                dimensions=dim_list,
                task_description=body.message,
            )
            system_prompt = result["system_prompt"]
            dimensions_used = json.dumps(result["dimensions_used"], ensure_ascii=False)
            prompt_snapshot = system_prompt
            coverage_stats = json.dumps(result["coverage_stats"], ensure_ascii=False)

            # Send metadata first
            metadata = {
                "type": "metadata",
                "metadata": {
                    "dimensions_used": result["dimensions_used"],
                    "coverage_stats": result["coverage_stats"],
                },
            }
            yield {"data": json.dumps(metadata, ensure_ascii=False)}

            # Stream from AI
            full_response = ""
            async for chunk in chat_stream(system_prompt, messages):
                if chunk["type"] == "token":
                    full_response += chunk["content"]
                    yield {"data": json.dumps({"type": "token", "content": chunk["content"]}, ensure_ascii=False)}
                elif chunk["type"] == "done":
                    full_response = chunk["content"]
                    yield {"data": json.dumps({"type": "done", "content": ""}, ensure_ascii=False)}
                elif chunk["type"] == "error":
                    yield {"data": json.dumps({"type": "error", "content": chunk["content"]}, ensure_ascii=False)}

            # Save assistant message
            assistant_now = datetime.now().isoformat()
            await db.execute(
                """INSERT INTO messages
                   (conversation_id, role, content, dimensions_used, prompt_snapshot, coverage_stats, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (body.conversation_id, "assistant", full_response,
                 dimensions_used, prompt_snapshot, coverage_stats, assistant_now),
            )
            # Update conversation title from first user message if it's still default
            cursor = await db.execute(
                "SELECT title FROM conversations WHERE id = ?", (body.conversation_id,)
            )
            conv = await cursor.fetchone()
            if conv and conv["title"] == "新对话":
                # Use first 30 chars of user message as title
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
