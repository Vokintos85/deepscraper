"""Structured logging helpers."""

from __future__ import annotations

import logging
from typing import Any, Dict

import structlog


def configure_logging(level: str = "INFO") -> None:
    """Configure structlog and stdlib logging."""

    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO), format="%(message)s")
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, level.upper(), logging.INFO)),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> "structlog.stdlib.BoundLogger":
    """Return a structured logger."""

    return structlog.get_logger(name)


def event_dict_from_exc(exc: BaseException) -> Dict[str, Any]:
    return {"exc_type": exc.__class__.__name__, "exc_msg": str(exc)}


__all__ = ["configure_logging", "get_logger", "event_dict_from_exc"]
