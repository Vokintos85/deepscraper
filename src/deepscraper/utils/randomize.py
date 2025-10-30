"""Randomization helpers for anti-bot hygiene."""

from __future__ import annotations

import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0 Safari/537.36",
]


def random_user_agent() -> str:
    return random.choice(USER_AGENTS)


def random_delay(base: float = 1.0) -> float:
    return random.uniform(base * 0.6, base * 1.4)


__all__ = ["random_user_agent", "random_delay"]
