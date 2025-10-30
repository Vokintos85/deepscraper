"""Redis-backed task queue utilities."""

from __future__ import annotations

from typing import Callable

from redis import Redis
from rq import Connection, Queue, Worker

from ..config import get_settings
from ..logging import get_logger

logger = get_logger(__name__)


def get_queue(name: str = "deepscraper") -> Queue:
    settings = get_settings()
    connection = Redis.from_url(settings.redis_url)
    return Queue(name, connection=connection)


def enqueue(job: Callable, *args, **kwargs) -> None:
    queue = get_queue()
    queue.enqueue(job, *args, **kwargs)


def worker() -> None:
    settings = get_settings()
    connection = Redis.from_url(settings.redis_url)
    with Connection(connection):
        worker = Worker(["deepscraper"])
        logger.info("worker_start")
        worker.work()


__all__ = ["get_queue", "enqueue", "worker"]
