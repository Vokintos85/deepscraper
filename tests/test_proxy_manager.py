from __future__ import annotations

import time

from deepscraper.proxy.manager import ProxyManager


def test_proxy_rotation() -> None:
    manager = ProxyManager(["http://a", "http://b"], cooldown_seconds=0.1)
    first = manager.get()
    second = manager.get()
    assert first != second
    manager.report_failure(first)
    time.sleep(0.2)
    retry = manager.get()
    assert retry in {"http://a", "http://b"}
