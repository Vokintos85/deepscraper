"""DOM extraction helpers."""

from __future__ import annotations

from typing import Dict, List

from bs4 import BeautifulSoup


def extract_with_selectors(html: str, selectors: List[Dict[str, str]]) -> Dict[str, List[str]]:
    soup = BeautifulSoup(html, "html.parser")
    results: Dict[str, List[str]] = {}
    for field in selectors:
        selector = field["selector"]
        attr = field.get("attr")
        elements = soup.select(selector)
        values = [el.get(attr) if attr else el.get_text(strip=True) for el in elements]
        results[field["name"]] = values
    return results


__all__ = ["extract_with_selectors"]
