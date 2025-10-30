"""CSV exporter."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Mapping

from ..config import get_settings


def export_to_csv(rows: Iterable[Mapping[str, str]], filename: str | None = None) -> Path:
    settings = get_settings()
    settings.export_dir.mkdir(parents=True, exist_ok=True)
    output = settings.export_dir / (filename or "export.csv")
    rows = list(rows)
    if not rows:
        output.write_text("")
        return output
    with output.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return output


__all__ = ["export_to_csv"]
