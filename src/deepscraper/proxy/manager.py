"""Proxy pool manager with rotation and backoff."""

from __future__ import annotations

import itertools
import random
import time
from dataclasses import dataclass, field
from typing import Dict, Iterable, Iterator, List, Optional

from tenacity import retry, stop_after_attempt, wait_exponential


@dataclass
class ProxyRecord:
    address: str
    last_used: float = 0.0
    failures: int = 0
    metadata: Dict[str, str] = field(default_factory=dict)


class ProxyManager:
    """Simple proxy pool with backoff support."""

    def __init__(self, proxies: Iterable[str], cooldown_seconds: float = 10.0) -> None:
        self._records: Dict[str, ProxyRecord] = {proxy: ProxyRecord(proxy) for proxy in proxies}
        self._cooldown_seconds = cooldown_seconds
        self._cycle: Iterator[str] = itertools.cycle(self._records.keys()) if self._records else iter(())

    def __len__(self) -> int:
        return len(self._records)

    def get(self) -> Optional[str]:
        if not self._records:
            return None
        for _ in range(len(self._records)):
            proxy = next(self._cycle)
            record = self._records[proxy]
            if time.monotonic() - record.last_used >= self._cooldown_seconds:
                record.last_used = time.monotonic()
                return record.address
        return None

    def report_failure(self, proxy: str) -> None:
        record = self._records.get(proxy)
        if not record:
            return
        record.failures += 1
        record.last_used = time.monotonic() + min(record.failures * self._cooldown_seconds, 120.0)

    def report_success(self, proxy: str) -> None:
        record = self._records.get(proxy)
        if not record:
            return
        record.failures = max(record.failures - 1, 0)
        record.last_used = time.monotonic()

    def random_choice(self) -> Optional[str]:
        if not self._records:
            return None
        return random.choice(list(self._records.keys()))

    def add_proxy(self, proxy: str) -> None:
        if proxy not in self._records:
            self._records[proxy] = ProxyRecord(proxy)
            self._cycle = itertools.cycle(self._records.keys())

    def remove_proxy(self, proxy: str) -> None:
        if proxy in self._records:
            del self._records[proxy]
            self._cycle = itertools.cycle(self._records.keys()) if self._records else iter(())


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=30))
def backoff_fetch(fetcher, *args, **kwargs):  # type: ignore[no-untyped-def]
    return fetcher(*args, **kwargs)


__all__ = ["ProxyManager", "ProxyRecord", "backoff_fetch"]
