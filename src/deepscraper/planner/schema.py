from pydantic import BaseModel
from typing import Optional, Literal

class WaitInstruction(BaseModel):
    type: Literal["network_idle", "selector_visible", "fixed"]
    selector: Optional[str] = None
    timeout_ms: int = 5000

class PlanStep(BaseModel):
    action: str
    target: Optional[str] = None
    value: Optional[str] = None
    wait: Optional[WaitInstruction] = None

class ExtractionField(BaseModel):
    name: str
    selector: str
    attr: Optional[str] = None
    required: bool = False

class PaginationInstruction(BaseModel):
    type: str
    selector: Optional[str] = None
    max_pages: int = 1

class PlanDocument(BaseModel):
    url: str
    goal: str
    steps: list[PlanStep]
    fields: list[ExtractionField]
    pagination: PaginationInstruction
