"""JSON exporter."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Mapping

from ..config import get_settings


def export_to_json(rows: Iterable[Mapping[str, str]], filename: str | None = None) -> Path:
    settings = get_settings()
    settings.export_dir.mkdir(parents=True, exist_ok=True)
    output = settings.export_dir / (filename or "export.json")
    data = list(rows)
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    return output


__all__ = ["export_to_json"]
