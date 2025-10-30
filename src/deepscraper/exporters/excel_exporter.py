"""Excel exporter."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Mapping

import pandas as pd

from ..config import get_settings


def export_to_excel(rows: Iterable[Mapping[str, str]], filename: str | None = None) -> Path:
    settings = get_settings()
    settings.export_dir.mkdir(parents=True, exist_ok=True)
    output = settings.export_dir / (filename or "export.xlsx")
    df = pd.DataFrame(list(rows))
    df.to_excel(output, index=False)
    return output


__all__ = ["export_to_excel"]
