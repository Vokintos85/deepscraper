"""FastAPI stub for health checks."""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="Deepscraper API", version="0.1.0")


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


__all__ = ["app"]
