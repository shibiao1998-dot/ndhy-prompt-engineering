"""System prompt assembler with positive/negative separation."""

from __future__ import annotations

from typing import Optional

# Priority labels
PRIORITY_LABELS = {1: "必须", 2: "建议", 3: "可选"}


def assemble_system_prompt(
    dimensions: list[dict],
    task_description: str,
    user_exclusions: Optional[str] = None,
) -> dict:
    """Assemble the system prompt from matched dimensions.

    Returns dict with keys:
    - system_prompt: full assembled prompt
    - positive_section: positive content section
    - constraint_section: constraint / negative content section
    - dimensions_used: list of dimension IDs
    - coverage_stats: coverage statistics
    """
    positive_by_priority: dict[int, list[dict]] = {1: [], 2: [], 3: []}
    negative_items: list[dict] = []

    for dim in dimensions:
        dim_id = dim.get("id", "")
        dim_name = dim.get("name", "")
        description = dim.get("description", "") or ""
        direction = dim.get("direction", "positive")
        priority = dim.get("priority", 2)

        if not description.strip():
            continue

        if direction == "positive":
            positive_by_priority.setdefault(priority, []).append({
                "id": dim_id,
                "name": dim_name,
                "content": description,
            })
        elif direction == "negative":
            negative_items.append({
                "id": dim_id,
                "name": dim_name,
                "content": description,
            })
        elif direction == "mixed":
            # Split mixed content: lines with ❌/不要/禁止/红线 → negative, rest → positive
            pos_lines = []
            neg_lines = []
            for line in description.split("\n"):
                stripped = line.strip()
                if any(kw in stripped for kw in ["❌", "不要", "禁止", "红线", "不能做", "不做"]):
                    neg_lines.append(line)
                else:
                    pos_lines.append(line)

            if pos_lines:
                positive_by_priority.setdefault(priority, []).append({
                    "id": dim_id,
                    "name": dim_name,
                    "content": "\n".join(pos_lines),
                })
            if neg_lines:
                negative_items.append({
                    "id": dim_id,
                    "name": dim_name,
                    "content": "\n".join(neg_lines),
                })

    # Build positive section
    positive_parts = []
    for p in [1, 2, 3]:
        items = positive_by_priority.get(p, [])
        if not items:
            continue
        label = PRIORITY_LABELS.get(p, str(p))
        positive_parts.append(f"## {_priority_header(p)}（{label}）")
        for item in items:
            positive_parts.append(f"### {item['id']} {item['name']}")
            positive_parts.append(item["content"])
            positive_parts.append("")

    positive_section = "\n".join(positive_parts).strip()

    # Build constraint section
    constraint_parts = []
    if negative_items:
        constraint_parts.append("### 红线与禁区")
        for item in negative_items:
            constraint_parts.append(f"**{item['id']} {item['name']}**")
            constraint_parts.append(item["content"])
            constraint_parts.append("")

    if user_exclusions:
        constraint_parts.append("### 排除条件")
        constraint_parts.append(user_exclusions)

    constraint_section = "\n".join(constraint_parts).strip()

    # Assemble full system prompt
    system_prompt = f"""你是华渔教育的 AI 设计师。你的任务是基于以下完整的信息上下文，
为用户产出专业级的设计方案。

## 核心原则
- 信息对称：你已获得最全面的项目信息，请充分利用
- 如果用户描述不够清晰，主动追问 2-4 个关键问题后再产出方案
- 追问应覆盖用户画像、使用场景、技术约束、竞品差异化等维度

## 正向信息（你需要遵循的方向）
{positive_section}

## 约束与禁忌（你必须避免的事项）
{constraint_section}

## 输出要求
1. 结构化 Markdown 格式
2. 包含：设计概述、用户旅程、交互方案、视觉建议、约束与禁忌
3. 方案应可直接用于项目推进
"""

    # Coverage stats
    total_dims = len(dimensions)
    used_dims = [d["id"] for d in dimensions if (d.get("description") or "").strip()]
    must_dims = [d for d in dimensions if d.get("priority") == 1]
    must_filled = [d for d in must_dims if (d.get("description") or "").strip()]
    suggest_dims = [d for d in dimensions if d.get("priority") == 2]
    suggest_filled = [d for d in suggest_dims if (d.get("description") or "").strip()]
    optional_dims = [d for d in dimensions if d.get("priority") == 3]
    optional_filled = [d for d in optional_dims if (d.get("description") or "").strip()]

    coverage_stats = {
        "total": total_dims,
        "used": len(used_dims),
        "coverage_rate": round(len(used_dims) / total_dims * 100, 1) if total_dims else 0,
        "must": {"total": len(must_dims), "filled": len(must_filled)},
        "suggest": {"total": len(suggest_dims), "filled": len(suggest_filled)},
        "optional": {"total": len(optional_dims), "filled": len(optional_filled)},
        "truncated": 0,
    }

    return {
        "system_prompt": system_prompt.strip(),
        "positive_section": positive_section,
        "constraint_section": constraint_section,
        "dimensions_used": used_dims,
        "coverage_stats": coverage_stats,
    }


def _priority_header(priority: int) -> str:
    """Return the section header for a given priority level."""
    return {1: "一级信息", 2: "二级信息", 3: "三级信息"}.get(priority, f"{priority}级信息")
