"""Multi-engine prompt format adapter."""

from __future__ import annotations


# Engine configurations
ENGINES = [
    {
        "id": "claude-opus-4-6",
        "name": "Claude Opus 4.6",
        "type": "通用 AI",
        "format": "结构化 Markdown",
        "max_chars": 200_000,
        "actual_call": True,
        "description": "当前主力引擎，通过 ndhy-gateway 实际调用",
    },
    {
        "id": "claude-sonnet-4-6",
        "name": "Claude Sonnet 4.6",
        "type": "通用 AI",
        "format": "结构化 Markdown",
        "max_chars": 200_000,
        "actual_call": False,
        "description": "轻量快速版本",
    },
    {
        "id": "gpt-4o",
        "name": "GPT-4o",
        "type": "通用 AI",
        "format": "结构化 Markdown",
        "max_chars": 128_000,
        "actual_call": False,
        "description": "OpenAI 旗舰",
    },
    {
        "id": "gpt-o3",
        "name": "GPT-o3",
        "type": "推理 AI",
        "format": "结构化 Markdown",
        "max_chars": 200_000,
        "actual_call": False,
        "description": "OpenAI 推理模型",
    },
    {
        "id": "gemini-2-5-pro",
        "name": "Gemini 2.5 Pro",
        "type": "通用 AI",
        "format": "结构化 Markdown",
        "max_chars": 1_000_000,
        "actual_call": False,
        "description": "Google 旗舰，超长上下文",
    },
    {
        "id": "deepseek-r1",
        "name": "DeepSeek R1",
        "type": "推理 AI",
        "format": "结构化 Markdown",
        "max_chars": 128_000,
        "actual_call": False,
        "description": "国产推理模型",
    },
    {
        "id": "midjourney-v7",
        "name": "Midjourney v7",
        "type": "图像生成",
        "format": "精简关键词",
        "max_chars": 4_000,
        "actual_call": False,
        "description": "设计视觉方案",
    },
    {
        "id": "dall-e-3",
        "name": "DALL-E 3",
        "type": "图像生成",
        "format": "精简关键词",
        "max_chars": 4_000,
        "actual_call": False,
        "description": "OpenAI 图像生成",
    },
    {
        "id": "suno-v4",
        "name": "Suno v4",
        "type": "音频生成",
        "format": "简洁描述",
        "max_chars": 2_000,
        "actual_call": False,
        "description": "教育音频/音乐",
    },
]

ENGINE_MAP = {e["id"]: e for e in ENGINES}


def adapt_prompt(prompt_text: str, engine_id: str) -> dict:
    """Adapt a prompt to a specific engine format.

    Returns dict with keys: adapted_prompt, engine_id, engine_name, format_type, max_chars, truncated
    """
    engine = ENGINE_MAP.get(engine_id)
    if not engine:
        return {
            "adapted_prompt": prompt_text,
            "engine_id": engine_id,
            "engine_name": "未知引擎",
            "format_type": "原始文本",
            "max_chars": 0,
            "truncated": False,
        }

    engine_type = engine["type"]
    max_chars = engine["max_chars"]

    if engine_type in ("通用 AI", "推理 AI"):
        adapted = _adapt_for_text_ai(prompt_text, max_chars)
    elif engine_type == "图像生成":
        adapted = _adapt_for_image(prompt_text, max_chars)
    elif engine_type == "音频生成":
        adapted = _adapt_for_audio(prompt_text, max_chars)
    else:
        adapted = prompt_text[:max_chars]

    truncated = len(prompt_text) > max_chars

    return {
        "adapted_prompt": adapted,
        "engine_id": engine_id,
        "engine_name": engine["name"],
        "format_type": engine["format"],
        "max_chars": max_chars,
        "truncated": truncated,
    }


def _adapt_for_text_ai(prompt: str, max_chars: int) -> str:
    """Adapt prompt for text-based AI engines (Markdown format)."""
    if len(prompt) <= max_chars:
        return prompt
    # Truncate lower-priority content
    return prompt[:max_chars - 50] + "\n\n[... 部分低优先级内容已截断 ...]"


def _adapt_for_image(prompt: str, max_chars: int) -> str:
    """Adapt prompt for image generation engines (keyword format)."""
    # Extract key visual concepts from the prompt
    lines = prompt.split("\n")
    keywords = []

    # Extract from headings and key lines
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Skip system-level instructions
        if line.startswith("你是") or line.startswith("##") and "原则" in line:
            continue
        # Extract from section headers
        if line.startswith("### "):
            keywords.append(line.replace("### ", "").strip())
        # Extract keywords from content with key markers
        elif any(kw in line for kw in ["风格", "颜色", "色彩", "视觉", "氛围", "场景", "用户", "设计"]):
            # Take the first meaningful part
            clean = line.strip("- ·•").strip()
            if len(clean) < 80:
                keywords.append(clean)

    if not keywords:
        keywords = ["教育设计", "专业", "现代"]

    result = ", ".join(keywords)
    if len(result) > max_chars:
        result = result[:max_chars - 3] + "..."
    return result


def _adapt_for_audio(prompt: str, max_chars: int) -> str:
    """Adapt prompt for audio generation engines (concise description)."""
    lines = prompt.split("\n")
    audio_parts = []

    for line in lines:
        line = line.strip()
        if any(kw in line for kw in ["氛围", "情感", "节奏", "音乐", "声音", "语调", "风格"]):
            clean = line.strip("- ·•").strip()
            if clean:
                audio_parts.append(clean)

    if not audio_parts:
        audio_parts = ["教育类背景音乐，专业、温暖、积极的氛围"]

    result = "。".join(audio_parts)
    if len(result) > max_chars:
        result = result[:max_chars - 3] + "..."
    return result


def get_all_engines() -> list[dict]:
    """Return all engine configurations."""
    return ENGINES
