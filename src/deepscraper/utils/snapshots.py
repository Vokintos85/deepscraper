"""HTML snapshot storage using MinIO."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

from ..config import get_settings


async def store_snapshot(project: str, html: str, path: Optional[Path] = None) -> Path:
    settings = get_settings()
    base_dir = Path("snapshots") / settings.minio_bucket / project
    if path is None:
        path = base_dir / f"{datetime.utcnow().isoformat()}.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    # Placeholder for MinIO upload; real implementation would use boto3/minio SDK.
    return path


__all__ = ["store_snapshot"]
