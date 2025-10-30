"""Network response capture helpers."""

from __future__ import annotations

from typing import Any, Dict, List


class NetworkCapture:
    """Collects network responses for later parsing."""

    def __init__(self) -> None:
        self._payloads: List[Dict[str, Any]] = []

    def record(self, request_url: str, response_json: Dict[str, Any]) -> None:
        self._payloads.append({"url": request_url, "json": response_json})

    def find_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        return [payload for payload in self._payloads if keyword in payload["url"]]

    @property
    def payloads(self) -> List[Dict[str, Any]]:
        return list(self._payloads)


__all__ = ["NetworkCapture"]
