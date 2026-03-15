"""Engines router — list available AI engines."""

from __future__ import annotations

from fastapi import APIRouter

from models import EngineResponse
from services.engine_adapter import get_all_engines

router = APIRouter(prefix="/api", tags=["engines"])


@router.get("/engines")
async def list_engines():
    """Return all engine configurations."""
    engines = get_all_engines()
    return [EngineResponse(**e) for e in engines]
