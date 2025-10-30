"""LLM-based extraction fallback stub."""

from __future__ import annotations

from typing import Any, Dict, List

from .dom import extract_with_selectors


def llm_guided_extraction(html: str, hints: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    return extract_with_selectors(html, hints)


__all__ = ["llm_guided_extraction"]
