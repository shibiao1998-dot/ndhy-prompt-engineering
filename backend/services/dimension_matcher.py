"""Dimension matching logic — uses AI to match task descriptions to dimensions."""

from __future__ import annotations

import json
from typing import Optional

from services.ai_service import chat_single


async def match_dimensions(
    task_description: str,
    all_dimensions: list[dict],
) -> list[dict]:
    """Match a task description to relevant dimensions using AI.

    Returns list of dicts: [{id, name, priority, reason}, ...]
    """
    # Build a compact dimension list for the AI
    dim_list = []
    for d in all_dimensions:
        dim_list.append(
            f"- {d['id']} | {d['name']} | 类别: {d.get('category_name', d['category'])} | "
            f"方向: {d.get('direction', 'positive')}"
        )
    dim_text = "\n".join(dim_list)

    system_prompt = """你是一个维度匹配专家。给定一个设计任务描述和可用的维度列表，
你需要判断哪些维度与该任务相关，并为每个匹配的维度分配优先级。

规则：
1. 优先级 1 = 必须（与任务核心直接相关）
2. 优先级 2 = 建议（有助于提升方案质量）
3. 优先级 3 = 可选（可能相关但非必需）
4. 不相关的维度不要列出

请严格以 JSON 数组格式返回，每个元素包含:
{"id": "维度ID", "priority": 数字, "reason": "简短原因"}

只返回 JSON 数组，不要其他文字。"""

    user_msg = f"""设计任务：{task_description}

可用维度列表：
{dim_text}"""

    response = await chat_single(
        system_prompt=system_prompt,
        messages=[{"role": "user", "content": user_msg}],
        max_tokens=4096,
        temperature=0.2,
    )

    # Parse AI response
    try:
        # Try to extract JSON from response
        text = response.strip()
        # Handle markdown code blocks
        if "```" in text:
            start = text.find("[")
            end = text.rfind("]") + 1
            if start >= 0 and end > start:
                text = text[start:end]
        matched = json.loads(text)
    except (json.JSONDecodeError, ValueError):
        # Fallback: return all dimensions with default priority
        matched = [{"id": d["id"], "priority": 2, "reason": "自动匹配"} for d in all_dimensions[:20]]

    # Enrich with dimension names
    dim_map = {d["id"]: d for d in all_dimensions}
    result = []
    for m in matched:
        dim_id = m.get("id", "")
        if dim_id in dim_map:
            result.append({
                "id": dim_id,
                "name": dim_map[dim_id]["name"],
                "priority": m.get("priority", 2),
                "reason": m.get("reason", ""),
            })

    return result
