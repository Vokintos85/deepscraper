"""Pydantic models describing scraping plans."""

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ExtractionField(BaseModel):
    name: str
    selector: str
    attr: Optional[str] = None
    required: bool = False


class WaitInstruction(BaseModel):
    type: Literal["network_idle", "selector", "delay"] = "network_idle"
    selector: Optional[str] = None
    timeout_ms: int = Field(default=5000, ge=0)


class PaginationInstruction(BaseModel):
    type: Literal["click", "scroll", "none"] = "none"
    selector: Optional[str] = None
    max_pages: int = Field(default=1, ge=1)


class PlanStep(BaseModel):
    action: Literal["navigate", "click", "fill", "wait", "extract"]
    target: Optional[str] = None
    value: Optional[str] = None
    wait: Optional[WaitInstruction] = None


class PlanDocument(BaseModel):
    url: str
    goal: str
    steps: List[PlanStep]
    fields: List[ExtractionField]
    pagination: PaginationInstruction = PaginationInstruction()


__all__ = [
    "ExtractionField",
    "WaitInstruction",
    "PaginationInstruction",
    "PlanStep",
    "PlanDocument",
]
