"""Claude API integration via OpenAI-compatible endpoint (streaming)."""

from __future__ import annotations

import json
from typing import AsyncGenerator

import httpx

API_BASE = "http://127.0.0.1:18795/v1"
API_KEY = "sk-nd-x0hURzXLt6ecXY5EAe524aFd016a48B58aCa75A5Af1e3"
MODEL = "claude-opus-4-6"


async def chat_stream(
    system_prompt: str,
    messages: list[dict],
) -> AsyncGenerator[dict, None]:
    """Stream chat completions from the Claude API.

    Yields dicts with keys: type ("token" | "done" | "error"), content.
    """
    payload = {
        "model": MODEL,
        "stream": True,
        "messages": [
            {"role": "system", "content": system_prompt},
            *messages,
        ],
        "max_tokens": 8192,
        "temperature": 0.7,
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    full_content = ""
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{API_BASE}/chat/completions",
                json=payload,
                headers=headers,
            ) as resp:
                if resp.status_code != 200:
                    body = await resp.aread()
                    yield {
                        "type": "error",
                        "content": f"API error {resp.status_code}: {body.decode()[:500]}",
                    }
                    return

                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data_str = line[6:]
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        token = delta.get("content", "")
                        if token:
                            full_content += token
                            yield {"type": "token", "content": token}
                    except (json.JSONDecodeError, IndexError, KeyError):
                        continue

        yield {"type": "done", "content": full_content}

    except httpx.ConnectError:
        yield {
            "type": "error",
            "content": "无法连接到 AI 服务 (127.0.0.1:18795)，请确认 ndhy-gateway 已启动。",
        }
    except Exception as e:
        yield {"type": "error", "content": f"AI 服务调用异常: {str(e)}"}


async def chat_single(
    system_prompt: str,
    messages: list[dict],
    max_tokens: int = 4096,
    temperature: float = 0.3,
) -> str:
    """Non-streaming single-shot chat completion. Used for dimension matching etc."""
    payload = {
        "model": MODEL,
        "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt},
            *messages,
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{API_BASE}/chat/completions",
                json=payload,
                headers=headers,
            )
            if resp.status_code != 200:
                return f"[AI 服务错误 {resp.status_code}]"
            data = resp.json()
            return data["choices"][0]["message"]["content"]
    except httpx.ConnectError:
        return "[无法连接到 AI 服务]"
    except Exception as e:
        return f"[AI 调用异常: {e}]"
