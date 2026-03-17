"""AIhub Platform Client — BTS Token auth + MAC signature + Chat/Workflow API.

Based on the AIhub integration guide. Handles:
- BTS Token acquisition and caching (2h TTL)
- MAC signature generation (HMAC-SHA256)
- Chat API calls (blocking + streaming)
- Automatic token refresh on 401
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from base64 import b64encode
from typing import AsyncGenerator, Optional
from urllib.parse import urlparse

import logging

import httpx

logger = logging.getLogger(__name__)

# ── Config from environment ──────────────────────────────────────────────

AIHUB_API_URL = os.getenv("AIHUB_API_URL", "https://ai-hub-api.aiae.ndhy.com")
AIHUB_PROJECT_KEY = os.getenv("AIHUB_PROJECT_KEY", "")
AIHUB_SDP_APP_ID = os.getenv("AIHUB_SDP_APP_ID", "b4fb92a0-af7f-49c2-b270-8f62afac1133")
AIHUB_BOT_ID = os.getenv("AIHUB_BOT_ID", "")  # The chatflow bot ID
AIHUB_WORKFLOW_BOT_ID = os.getenv("AIHUB_WORKFLOW_BOT_ID", "")  # Workflow bot ID (dimension update)
AIHUB_ANALYZE_BOT_ID = os.getenv("AIHUB_ANALYZE_BOT_ID", "")  # Workflow bot ID (dimension analysis)

# Log config at import time
logger.info(f"[AIhub Config] API URL: {AIHUB_API_URL}")
logger.info(f"[AIhub Config] Chatflow Bot ID: {AIHUB_BOT_ID}")
logger.info(f"[AIhub Config] Workflow Bot ID: {AIHUB_WORKFLOW_BOT_ID}")
logger.info(f"[AIhub Config] Analyze Bot ID: {AIHUB_ANALYZE_BOT_ID}")

BTS_API_URL = os.getenv("BTS_API_URL", "https://ucbts.101.com")
BTS_APP_NAME = os.getenv("BTS_APP_NAME", "ai-ceo-poc")
BTS_APP_SECRET = os.getenv("BTS_APP_SECRET", "")

# Pre-cached token (optional, avoids initial BTS call)
_cached_token: Optional[str] = os.getenv("BTS_TOKEN")
_cached_mac_key: Optional[str] = os.getenv("BTS_MAC_KEY")
_token_expires_at: float = 0.0


# ── BTS Token Management ────────────────────────────────────────────────

async def _fetch_bts_token() -> tuple[str, str]:
    """Fetch a new BTS token from the BTS API.

    Tries the /v1/tokens endpoint (from get-new-bts-token.js script) first,
    falls back to /v0.1/token/apply (from integration guide) if it fails.

    Returns (access_token, mac_key).
    """
    timestamp = int(time.time() * 1000)

    # Method 1: Script format — sign = HMAC(appName:timestamp), endpoint /v1/tokens
    sign_string_v1 = f"{BTS_APP_NAME}:{timestamp}"
    sign_v1 = hmac.new(
        BTS_APP_SECRET.encode("utf-8"),
        sign_string_v1.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    sign_v1_b64 = b64encode(sign_v1).decode("utf-8")

    payload_v1 = {
        "app_name": BTS_APP_NAME,
        "app_secret": BTS_APP_SECRET,
        "token_type": "e",
        "timestamp": timestamp,
        "sign": sign_v1_b64,
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        # Try v1 first
        try:
            resp = await client.post(
                f"{BTS_API_URL}/v1/tokens",
                json=payload_v1,
                headers={"Content-Type": "application/json"},
            )
            if resp.status_code == 200:
                data = resp.json()
                access_token = data.get("access_token")
                mac_key = data.get("mac_key")
                if access_token and mac_key:
                    return access_token, mac_key
        except Exception:
            pass

        # Fallback: Guide format — sign = HMAC(appName + timestamp), endpoint /v0.1/token/apply
        sign_string_v0 = f"{BTS_APP_NAME}{timestamp}"
        sign_v0 = hmac.new(
            BTS_APP_SECRET.encode("utf-8"),
            sign_string_v0.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        sign_v0_b64 = b64encode(sign_v0).decode("utf-8")

        payload_v0 = {
            "app_name": BTS_APP_NAME,
            "timestamp": timestamp,
            "sign": sign_v0_b64,
            "token_type": "e",
        }

        resp = await client.post(
            f"{BTS_API_URL}/v0.1/token/apply",
            json=payload_v0,
            headers={"Content-Type": "application/json"},
        )
        resp.raise_for_status()
        data = resp.json()

    access_token = data.get("access_token")
    mac_key = data.get("mac_key")
    if not access_token or not mac_key:
        raise RuntimeError(f"BTS token response missing fields: {data}")
    return access_token, mac_key


async def get_bts_credentials() -> tuple[str, str]:
    """Get valid BTS token + mac_key, refreshing if needed.

    Returns (token, mac_key).
    """
    global _cached_token, _cached_mac_key, _token_expires_at

    now = time.time()
    # Refresh if expired or will expire within 5 minutes
    if _cached_token and _cached_mac_key and now < _token_expires_at - 300:
        return _cached_token, _cached_mac_key

    token, mac_key = await _fetch_bts_token()
    _cached_token = token
    _cached_mac_key = mac_key
    _token_expires_at = now + 7200  # 2 hours
    return token, mac_key


# ── MAC Signature ────────────────────────────────────────────────────────

def _generate_mac_signature(
    mac_key: str,
    method: str,
    path: str,
    host: str,
    nonce: str,
) -> str:
    """Generate MAC signature for AIhub API authentication.

    Signature base: nonce\nmethod\npath\nhost\nsdp_app_id\n
    """
    signature_base = f"{nonce}\n{method}\n{path}\n{host}\n{AIHUB_SDP_APP_ID}\n"
    sig = hmac.new(
        mac_key.encode("utf-8"),
        signature_base.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return b64encode(sig).decode("utf-8")


def _build_auth_header(token: str, mac_key: str, method: str, path: str) -> str:
    """Build the Authorization header for AIhub API."""
    parsed = urlparse(AIHUB_API_URL)
    host = parsed.netloc
    nonce = str(int(time.time() * 1000))
    mac = _generate_mac_signature(mac_key, method, path, host, nonce)
    return f'BTS id="{token}",nonce="{nonce}",mac="{mac}"'


def _build_headers(token: str, mac_key: str, method: str, path: str) -> dict:
    """Build full request headers for AIhub API."""
    return {
        "Content-Type": "application/json",
        "X-App-Id": AIHUB_BOT_ID,
        "X-Project-Key": AIHUB_PROJECT_KEY,
        "sdp-app-id": AIHUB_SDP_APP_ID,
        "Authorization": _build_auth_header(token, mac_key, method, path),
    }


# ── Chat API ─────────────────────────────────────────────────────────────

async def chat_blocking(
    query: str,
    user: str = "default-user",
    conversation_id: Optional[str] = None,
    inputs: Optional[dict] = None,
) -> dict:
    """Call AIhub Chat API in blocking mode.

    Returns the full response dict.
    """
    token, mac_key = await get_bts_credentials()
    path = "/v1/chat-messages"

    payload = {
        "query": query,
        "inputs": inputs or {},
        "user": user,
        "response_mode": "blocking",
    }
    if conversation_id:
        payload["conversation_id"] = conversation_id

    headers = _build_headers(token, mac_key, "POST", path)

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            f"{AIHUB_API_URL}{path}",
            json=payload,
            headers=headers,
        )
        if resp.status_code == 401:
            # Token expired, refresh and retry once
            global _token_expires_at
            _token_expires_at = 0
            token, mac_key = await get_bts_credentials()
            headers = _build_headers(token, mac_key, "POST", path)
            resp = await client.post(
                f"{AIHUB_API_URL}{path}",
                json=payload,
                headers=headers,
            )
        resp.raise_for_status()
        return resp.json()


async def chat_stream(
    query: str,
    user: str = "default-user",
    conversation_id: Optional[str] = None,
    inputs: Optional[dict] = None,
) -> AsyncGenerator[dict, None]:
    """Call AIhub Chat API in streaming mode.

    Yields dicts: {"type": "token"|"done"|"error"|"metadata", ...}
    """
    token, mac_key = await get_bts_credentials()
    path = "/v1/chat-messages"

    payload = {
        "query": query,
        "inputs": inputs or {},
        "user": user,
        "response_mode": "streaming",
    }
    if conversation_id:
        payload["conversation_id"] = conversation_id

    headers = _build_headers(token, mac_key, "POST", path)

    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            async with client.stream(
                "POST",
                f"{AIHUB_API_URL}{path}",
                json=payload,
                headers=headers,
            ) as resp:
                if resp.status_code == 401:
                    yield {"type": "error", "content": "BTS Token 过期，请刷新后重试"}
                    return
                if resp.status_code != 200:
                    body = await resp.aread()
                    yield {"type": "error", "content": f"AIhub API 错误 {resp.status_code}: {body.decode()[:500]}"}
                    return

                conversation_id_from_response = None
                full_content = ""

                async for line in resp.aiter_lines():
                    line = line.strip()
                    if not line or not line.startswith("data:"):
                        continue

                    data_str = line[5:].strip()
                    if not data_str:
                        continue

                    try:
                        event = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    event_type = event.get("event", "")

                    if event_type == "message":
                        # Streaming token
                        answer = event.get("answer", "")
                        if answer:
                            full_content += answer
                            yield {"type": "token", "content": answer}

                        # Capture conversation_id from first message event
                        if not conversation_id_from_response:
                            conversation_id_from_response = event.get("conversation_id")
                            if conversation_id_from_response:
                                yield {
                                    "type": "metadata",
                                    "conversation_id": conversation_id_from_response,
                                    "message_id": event.get("message_id", ""),
                                }

                    elif event_type == "message_end":
                        cid = event.get("conversation_id", conversation_id_from_response)
                        yield {
                            "type": "done",
                            "content": full_content,
                            "conversation_id": cid,
                            "message_id": event.get("message_id", ""),
                            "metadata": event.get("metadata", {}),
                        }
                        return

                    elif event_type == "error":
                        yield {"type": "error", "content": event.get("message", "Unknown error")}
                        return

                    elif event_type == "ping":
                        continue

                # If stream ended without message_end
                if full_content:
                    yield {
                        "type": "done",
                        "content": full_content,
                        "conversation_id": conversation_id_from_response,
                    }

    except httpx.ConnectError:
        yield {"type": "error", "content": f"无法连接到 AIhub API ({AIHUB_API_URL})"}
    except httpx.ReadTimeout:
        yield {"type": "error", "content": "AIhub API 响应超时，请稍后重试"}
    except Exception as e:
        yield {"type": "error", "content": f"AIhub 调用异常: {str(e)}"}


# ── Workflow API ──────────────────────────────────────────────────────

def _build_workflow_headers(token: str, mac_key: str, method: str, path: str) -> dict:
    """Build request headers for AIhub Workflow API (uses WORKFLOW_BOT_ID)."""
    return {
        "Content-Type": "application/json",
        "X-App-Id": AIHUB_WORKFLOW_BOT_ID,
        "X-Project-Key": AIHUB_PROJECT_KEY,
        "sdp-app-id": AIHUB_SDP_APP_ID,
        "Authorization": _build_auth_header(token, mac_key, method, path),
    }


async def workflow_blocking(
    dimension_input: str,
    user: str = "dimension-updater",
) -> dict:
    """Call AIhub Workflow API in streaming mode (to avoid SSL gateway timeout).

    Sends dimension_input and collects SSE events until workflow_finished.
    Expects outputs:
    - dimension_definition: Updated definition text
    - source_explanation: Detailed source explanation

    Returns dict with output keys.
    """
    if not AIHUB_WORKFLOW_BOT_ID:
        raise RuntimeError("AIHUB_WORKFLOW_BOT_ID 未配置，请在 .env 中设置")

    token, mac_key = await get_bts_credentials()
    path = "/v1/workflows/run"

    payload = {
        "inputs": {
            "dimension_input": dimension_input,
        },
        "user": user,
        "response_mode": "streaming",
    }

    headers = _build_workflow_headers(token, mac_key, "POST", path)

    outputs = {}

    try:
        async with httpx.AsyncClient(timeout=1200.0) as client:  # 20 min timeout for workflow
            async with client.stream(
                "POST",
                f"{AIHUB_API_URL}{path}",
                json=payload,
                headers=headers,
            ) as resp:
                if resp.status_code == 401:
                    # Token expired, refresh and retry
                    global _token_expires_at
                    _token_expires_at = 0
                    raise RuntimeError("BTS Token 过期")

                if resp.status_code != 200:
                    body = await resp.aread()
                    raise RuntimeError(f"Workflow API 错误 {resp.status_code}: {body.decode()[:500]}")

                async for line in resp.aiter_lines():
                    line = line.strip()
                    if not line or not line.startswith("data:"):
                        continue

                    data_str = line[5:].strip()
                    if not data_str:
                        continue

                    try:
                        event = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    event_type = event.get("event", "")

                    if event_type == "workflow_finished":
                        # Final event with outputs
                        event_outputs = event.get("data", {}).get("outputs", {})
                        if event_outputs:
                            outputs = event_outputs
                        break

                    elif event_type == "node_finished":
                        # Some workflows put outputs in node_finished events
                        node_outputs = event.get("data", {}).get("outputs", {})
                        if node_outputs:
                            # Merge outputs from each node
                            outputs.update(node_outputs)

                    elif event_type == "error":
                        raise RuntimeError(f"Workflow error: {event.get('message', 'Unknown')}")

                    elif event_type == "ping":
                        continue

    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"Workflow 连接异常: {type(e).__name__}: {str(e)}")

    return {
        "dimension_definition": outputs.get("dimension_definition", ""),
        "source_explanation": outputs.get("source_explanation", ""),
        "raw_response": outputs,
    }


# ── Dimension Analysis Workflow API ───────────────────────────────────

def _build_analyze_headers(token: str, mac_key: str, method: str, path: str) -> dict:
    """Build request headers for AIhub Analyze Workflow (uses ANALYZE_BOT_ID)."""
    return {
        "Content-Type": "application/json",
        "X-App-Id": AIHUB_ANALYZE_BOT_ID,
        "X-Project-Key": AIHUB_PROJECT_KEY,
        "sdp-app-id": AIHUB_SDP_APP_ID,
        "Authorization": _build_auth_header(token, mac_key, method, path),
    }


async def analyze_dimensions_workflow(
    user_query: str,
    dimension_list: str,
    user: str = "dimension-analyzer",
) -> list[str]:
    """Call AIhub Dimension Analysis Workflow to select relevant dimensions.

    Sends user_query + dimension_list, expects back selected_dimension_ids as JSON array.
    Returns list of dimension IDs like ["A01", "B04", "C01"].
    """
    logger.info(f"[Analyze] ========== START DIMENSION ANALYSIS ==========")
    logger.info(f"[Analyze] Bot ID: {AIHUB_ANALYZE_BOT_ID}")
    logger.info(f"[Analyze] User query: {user_query[:100]}")
    logger.info(f"[Analyze] Dimension list length: {len(dimension_list)} chars")

    if not AIHUB_ANALYZE_BOT_ID:
        logger.error("[Analyze] AIHUB_ANALYZE_BOT_ID is EMPTY! Workflow will not be called.")
        raise RuntimeError("AIHUB_ANALYZE_BOT_ID 未配置，请在 .env 中设置")

    token, mac_key = await get_bts_credentials()
    path = "/v1/workflows/run"

    payload = {
        "inputs": {
            "user_query": user_query,
            "dimension_list": dimension_list,
        },
        "user": user,
        "response_mode": "streaming",
    }

    headers = _build_analyze_headers(token, mac_key, "POST", path)
    logger.info(f"[Analyze] Sending to {AIHUB_API_URL}{path}")
    logger.info(f"[Analyze] Headers X-App-Id: {headers.get('X-App-Id', 'MISSING')}")

    outputs = {}

    try:
        async with httpx.AsyncClient(timeout=1200.0) as client:  # 20 min timeout
            async with client.stream(
                "POST",
                f"{AIHUB_API_URL}{path}",
                json=payload,
                headers=headers,
            ) as resp:
                logger.info(f"[Analyze] Response status: {resp.status_code}")

                if resp.status_code == 401:
                    global _token_expires_at
                    _token_expires_at = 0
                    raise RuntimeError("BTS Token 过期")

                if resp.status_code != 200:
                    body = await resp.aread()
                    error_text = body.decode("utf-8", errors="replace")[:500]
                    logger.error(f"[Analyze] API error: {resp.status_code} — {error_text}")
                    raise RuntimeError(f"Analyze Workflow API 错误 {resp.status_code}: {error_text}")

                event_count = 0
                async for line in resp.aiter_lines():
                    line = line.strip()
                    if not line or not line.startswith("data:"):
                        continue

                    data_str = line[5:].strip()
                    if not data_str:
                        continue

                    try:
                        event = json.loads(data_str)
                    except json.JSONDecodeError:
                        logger.warning(f"[Analyze] Bad JSON: {data_str[:200]}")
                        continue

                    event_type = event.get("event", "")
                    event_count += 1
                    logger.info(f"[Analyze] Event #{event_count}: {event_type}")

                    if event_type == "workflow_finished":
                        event_outputs = event.get("data", {}).get("outputs", {})
                        logger.info(f"[Analyze] workflow_finished outputs keys: {list(event_outputs.keys())}")
                        if event_outputs:
                            outputs = event_outputs
                        break

                    elif event_type == "node_finished":
                        node_outputs = event.get("data", {}).get("outputs", {})
                        if node_outputs:
                            logger.info(f"[Analyze] node_finished outputs keys: {list(node_outputs.keys())}")
                            outputs.update(node_outputs)

                    elif event_type == "error":
                        error_msg = event.get("message", "Unknown")
                        logger.error(f"[Analyze] Workflow error event: {error_msg}")
                        raise RuntimeError(f"Analyze Workflow error: {error_msg}")

                    elif event_type == "ping":
                        continue

                logger.info(f"[Analyze] Stream done, {event_count} events, outputs keys: {list(outputs.keys())}")

    except RuntimeError:
        raise
    except Exception as e:
        logger.error(f"[Analyze] Connection exception: {type(e).__name__}: {str(e)}")
        raise RuntimeError(f"Analyze Workflow 连接异常: {type(e).__name__}: {str(e)}")

    # Parse selected_dimension_ids from outputs
    raw_ids = outputs.get("selected_dimension_ids", "")
    logger.info(f"[Analyze] raw_ids type={type(raw_ids).__name__}, value={str(raw_ids)[:300]}")

    if isinstance(raw_ids, list):
        logger.info(f"[Analyze] ========== SUCCESS: {len(raw_ids)} dimensions ==========")
        return raw_ids

    # Try to parse as JSON string
    if isinstance(raw_ids, str):
        raw_ids = raw_ids.strip()
        try:
            parsed = json.loads(raw_ids)
            if isinstance(parsed, list):
                result = [str(x) for x in parsed]
                logger.info(f"[Analyze] ========== SUCCESS (parsed JSON): {len(result)} dimensions ==========")
                return result
            if isinstance(parsed, dict) and "selected_dimension_ids" in parsed:
                result = [str(x) for x in parsed["selected_dimension_ids"]]
                logger.info(f"[Analyze] ========== SUCCESS (nested JSON): {len(result)} dimensions ==========")
                return result
        except json.JSONDecodeError:
            pass

    logger.error(f"[Analyze] ========== FAILED: unexpected output format ==========")
    logger.error(f"[Analyze] Full outputs: {str(outputs)[:500]}")
    raise RuntimeError(f"维度分析 Workflow 返回格式异常: {str(outputs)[:500]}")
