"""Playwright browser controller."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, List, Optional

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from ..config import get_settings
from ..logging import get_logger
from ..proxy.manager import ProxyManager
from ..utils.randomize import random_user_agent
from ..utils.timing import jitter

logger = get_logger(__name__)


class BrowserRunner:
    """Wraps Playwright interactions for plan execution."""

    def __init__(self, proxy_manager: Optional[ProxyManager] = None) -> None:
        self._settings = get_settings()
        self._proxy_manager = proxy_manager
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

    @asynccontextmanager
    async def context(self) -> AsyncIterator[Page]:
        playwright = await async_playwright().start()
        proxy = self._proxy_manager.get() if self._proxy_manager else None
        browser = await playwright.chromium.launch(headless=self._settings.headless, proxy={"server": proxy} if proxy else None)
        context = await browser.new_context(
            user_agent=random_user_agent(),
            viewport={"width": 1366, "height": 768},
        )
        page = await context.new_page()
        try:
            yield page
        finally:
            await context.close()
            await browser.close()
            await playwright.stop()

    async def navigate(self, page: Page, url: str) -> None:
        logger.info("navigate", url=url)
        await page.goto(url, wait_until="networkidle", timeout=self._settings.page_timeout)

    async def wait(self, page: Page, wait_config: Dict[str, Any]) -> None:
        wait_type = wait_config.get("type", "network_idle")
        timeout = wait_config.get("timeout_ms", 5_000)
        if wait_type == "selector" and wait_config.get("selector"):
            await page.wait_for_selector(wait_config["selector"], timeout=timeout)
        elif wait_type == "delay":
            await asyncio.sleep(timeout / 1000.0)
        else:
            await page.wait_for_load_state("networkidle", timeout=timeout)

    async def extract_fields(self, page: Page, fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        for field in fields:
            selector = field["selector"]
            attr = field.get("attr")
            values = await page.eval_on_selector_all(
                selector,
                "(elements, attr) => elements.map(el => attr ? el.getAttribute(attr) : el.innerText.trim())",
                arg=attr,
            )
            items.append({"name": field["name"], "values": values})
        return items

    async def paginate(self, page: Page, pagination: Dict[str, Any]) -> None:
        if pagination.get("type") == "click" and pagination.get("selector"):
            await page.click(pagination["selector"])
            await asyncio.sleep(jitter(2.0, 0.5))
        elif pagination.get("type") == "scroll":
            await page.mouse.wheel(0, 2000)
            await asyncio.sleep(jitter(1.0, 0.3))


__all__ = ["BrowserRunner"]
