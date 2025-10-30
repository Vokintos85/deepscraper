"""Minimal DeepSeek client wrapper."""

from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from ..config import get_settings
from .schema import ExtractionField, PaginationInstruction, PlanDocument, PlanStep, WaitInstruction


class DeepSeekClient:
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None) -> None:
        settings = get_settings()
        self._base_url = base_url or settings.deepseek_base_url
        self._api_key = api_key or settings.deepseek_api_key
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=60.0)

    async def generate_plan(self, url: str, goal: str) -> PlanDocument:
        if not self._api_key:
            return self._heuristic_plan(url, goal)
        response = await self._client.post(
            "/plans",
            json={"url": url, "goal": goal},
            headers={"Authorization": f"Bearer {self._api_key}"},
        )
        response.raise_for_status()
        data = response.json()
        return PlanDocument.model_validate(data)

    def _heuristic_plan(self, url: str, goal: str) -> PlanDocument:
        fields = [
            ExtractionField(name="title", selector="h1, h2, .product-title"),
            ExtractionField(name="price", selector=".price, [data-price]"),
            ExtractionField(name="sku", selector="[data-sku], .sku, .product-sku"),
        ]
        steps = [
            PlanStep(action="navigate", target=url),
            PlanStep(action="wait", wait=WaitInstruction(type="network_idle", timeout_ms=5000)),
            PlanStep(action="extract"),
        ]
        pagination = PaginationInstruction(type="scroll", max_pages=1)
        return PlanDocument(url=url, goal=goal, steps=steps, fields=fields, pagination=pagination)

    async def aclose(self) -> None:
        await self._client.aclose()


__all__ = ["DeepSeekClient"]
