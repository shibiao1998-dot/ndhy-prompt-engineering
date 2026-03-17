"""Pydantic models for request/response validation."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ─── Dimension ───────────────────────────────────────────────

class DimensionBase(BaseModel):
    name: str
    category: str
    category_name: Optional[str] = None
    description: Optional[str] = None
    data_source: Optional[str] = None
    update_frequency: Optional[str] = None
    direction: str = "positive"
    priority: int = 2
    raw_content: Optional[str] = None


class DimensionCreate(DimensionBase):
    id: str


class DimensionUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    category_name: Optional[str] = None
    description: Optional[str] = None
    quality_role: Optional[str] = None
    data_source: Optional[str] = None
    update_frequency: Optional[str] = None
    source_explanation: Optional[str] = None
    direction: Optional[str] = None
    priority: Optional[int] = None
    raw_content: Optional[str] = None


class WorkflowRequest(BaseModel):
    """Request body for triggering dimension update workflow."""
    dimension_id: str
    dimension_input: str  # Concatenated fields sent to workflow


class DimensionResponse(BaseModel):
    id: str
    name: str
    category: str
    category_name: Optional[str] = None
    description: Optional[str] = None
    pending_description: Optional[str] = None
    data_source: Optional[str] = None
    update_frequency: Optional[str] = None
    direction: str = "positive"
    priority: int = 2
    last_updated_at: Optional[str] = None
    review_status: str = "approved"
    reviewer: Optional[str] = None
    reviewed_at: Optional[str] = None
    created_at: Optional[str] = None
    raw_content: Optional[str] = None


# ─── Review ──────────────────────────────────────────────────

class ReviewRequest(BaseModel):
    action: str  # "approve" | "reject"
    reviewer: str
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    dimension_id: str
    action: str
    review_status: str
    message: str


# ─── Chat ────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    conversation_id: str
    message: str


class ConversationCreate(BaseModel):
    title: Optional[str] = None


class ConversationResponse(BaseModel):
    id: str
    title: Optional[str] = None
    task_type: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class MessageResponse(BaseModel):
    id: int
    conversation_id: str
    role: str
    content: str
    dimensions_used: Optional[str] = None
    prompt_snapshot: Optional[str] = None
    coverage_stats: Optional[str] = None
    created_at: Optional[str] = None


# ─── Match ───────────────────────────────────────────────────

class MatchRequest(BaseModel):
    task_description: str


class MatchedDimension(BaseModel):
    id: str
    name: str
    priority: int
    reason: Optional[str] = None


class MatchResponse(BaseModel):
    matched_dimensions: list[MatchedDimension]
    total_matched: int


# ─── Prompt ──────────────────────────────────────────────────

class PromptPreviewRequest(BaseModel):
    dimension_ids: list[str]
    task_description: str


class PromptPreviewResponse(BaseModel):
    system_prompt: str
    positive_section: str
    constraint_section: str
    dimensions_used: list[str]
    coverage_stats: dict


class PromptAdaptRequest(BaseModel):
    prompt_text: str
    engine_id: str


class PromptAdaptResponse(BaseModel):
    adapted_prompt: str
    engine_id: str
    engine_name: str
    format_type: str
    max_chars: int
    truncated: bool


# ─── Engine ──────────────────────────────────────────────────

class EngineResponse(BaseModel):
    id: str
    name: str
    type: str
    format: str
    max_chars: int
    actual_call: bool
    description: str


# ─── Stats ───────────────────────────────────────────────────

class CategoryStat(BaseModel):
    category: str
    category_name: Optional[str] = None
    total: int
    filled: int
    fill_rate: float  # 0.0 ~ 1.0


class DimensionStats(BaseModel):
    total_dimensions: int
    total_categories: int
    filled_dimensions: int
    unfilled_dimensions: int
    overall_fill_rate: float  # 0.0 ~ 1.0
    by_category: list[CategoryStat]
