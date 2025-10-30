# src/deepscraper/utils/stealth.py
"""Stealth techniques for avoiding bot detection."""

from __future__ import annotations

import random
from typing import Dict


class StealthManager:
    """Manages stealth techniques for browser automation."""

    def __init__(self):
        self._user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        ]

        self._viewports = [
            {"width": 1920, "height": 1080},
            {"width": 1366, "height": 768},
            {"width": 1536, "height": 864},
            {"width": 1440, "height": 900},
        ]

    def get_random_user_agent(self) -> str:
        """Get random user agent."""
        return random.choice(self._user_agents)

    def get_random_viewport(self) -> Dict[str, int]:
        """Get random viewport size."""
        return random.choice(self._viewports)


# Singleton instance
_stealth_manager = StealthManager()

def get_stealth_manager() -> StealthManager:
    """Get stealth manager instance."""
    return _stealth_manager


__all__ = ["StealthManager", "get_stealth_manager"]