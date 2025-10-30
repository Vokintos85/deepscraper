# src/deepscraper/runner/browser.py
"""Playwright browser controller."""

from __future__ import annotations

import asyncio
import base64
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, List, Optional

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from ..config import get_settings
from ..logging import get_logger
from ..proxy.manager import ProxyManager
from ..utils.randomize import random_user_agent
from ..utils.timing import jitter
from ..captcha.base import get_solver
from ..utils.stealth import get_stealth_manager

logger = get_logger(__name__)


class BrowserRunner:
    """Wraps Playwright interactions for plan execution."""

    def __init__(self, proxy_manager: Optional[ProxyManager] = None) -> None:
        self._settings = get_settings()
        self._proxy_manager = proxy_manager
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

        # Инициализируем капча-сервис
        self.captcha_solver = get_solver(
            self._settings.captcha_provider,
            self._settings.captcha_api_key
        )

    @asynccontextmanager
    async def context(self) -> AsyncIterator[Page]:
        playwright = await async_playwright().start()
        proxy = self._proxy_manager.get() if self._proxy_manager else None
        browser = await playwright.chromium.launch(headless=self._settings.headless, proxy={"server": proxy} if proxy else None)

        # ПРИМЕНЯЕМ STEALTH К КОНТЕКСТУ
        stealth_manager = get_stealth_manager()
        context = await browser.new_context(
            user_agent=stealth_manager.get_random_user_agent(),
            viewport=stealth_manager.get_random_viewport(),
        )

        # ДОБАВЛЯЕМ STEALTH СКРИПТ В КОНТЕКСТ
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
        """)

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

    # НОВЫЕ МЕТОДЫ ДЛЯ РАБОТЫ С КАПЧАМИ
    async def detect_and_solve_captcha(self, page: Page) -> bool:
        """Обнаруживает и решает капчи на странице."""
        logger.info("captcha_detection_started")

        # Проверяем наличие reCAPTCHA
        recaptcha_frames = await page.query_selector_all('iframe[src*="google.com/recaptcha"]')
        if recaptcha_frames:
            logger.info("recaptcha_detected")
            await self._solve_recaptcha(page)
            return True

        # Проверяем наличие hCaptcha
        hcaptcha_frames = await page.query_selector_all('iframe[src*="hcaptcha.com"]')
        if hcaptcha_frames:
            logger.info("hcaptcha_detected")
            await self._solve_hcaptcha(page)
            return True

        # Проверяем наличие image captcha
        captcha_images = await page.query_selector_all('img[src*="captcha"], img[alt*="captcha"]')
        if captcha_images:
            logger.info("image_captcha_detected")
            await self._solve_image_captcha(page, captcha_images[0])
            return True

        return False

    async def _solve_recaptcha(self, page: Page) -> None:
        """Решает reCAPTCHA."""
        try:
            # Получаем sitekey и URL
            site_key = await page.evaluate("""
                () => {
                    const recaptcha = document.querySelector('.g-recaptcha');
                    return recaptcha ? recaptcha.getAttribute('data-sitekey') : null;
                }
            """)

            if not site_key:
                # Пробуем найти в iframe
                site_key = await page.evaluate("""
                    () => {
                        const iframe = document.querySelector('iframe[src*="google.com/recaptcha"]');
                        if (iframe) {
                            const src = iframe.src;
                            const match = src.match(/[&?]k=([^&]+)/);
                            return match ? match[1] : null;
                        }
                        return null;
                    }
                """)

            if site_key:
                url = page.url
                logger.info("solving_recaptcha", site_key=site_key, url=url)

                # Решаем капчу
                token = await self.captcha_solver.solve_recaptcha_v2(site_key, url)
                logger.info("recaptcha_solved", token=token[:50] + "...")

                # Вводим токен
                await page.evaluate("""
                    (token) => {
                        // Ищем элемент для ввода токена
                        const responseElement = document.getElementById('g-recaptcha-response') ||
                                               document.querySelector('[name="g-recaptcha-response"]');
                        if (responseElement) {
                            responseElement.value = token;
                            const event = new Event('change', { bubbles: true });
                            responseElement.dispatchEvent(event);
                        }
                    }
                """, token)

                logger.info("recaptcha_token_applied")

        except Exception as e:
            logger.error("recaptcha_solve_failed", error=str(e))
            raise

    async def _solve_hcaptcha(self, page: Page) -> None:
        """Решает hCaptcha."""
        try:
            # Получаем sitekey
            site_key = await page.evaluate("""
                () => {
                    const iframe = document.querySelector('iframe[src*="hcaptcha.com"]');
                    if (iframe) {
                        const src = iframe.src;
                        const match = src.match(/[&?]sitekey=([^&]+)/);
                        return match ? match[1] : null;
                    }
                    return null;
                }
            """)

            if site_key:
                url = page.url
                logger.info("solving_hcaptcha", site_key=site_key, url=url)

                # Решаем капчу
                token = await self.captcha_solver.solve_hcaptcha(site_key, url)
                logger.info("hcaptcha_solved", token=token[:50] + "...")

                # Вводим токен (hCaptcha использует другой элемент)
                await page.evaluate("""
                    (token) => {
                        // hCaptcha обычно использует textarea с именем h-captcha-response
                        const responseElement = document.querySelector('textarea[name="h-captcha-response"]');
                        if (responseElement) {
                            responseElement.value = token;
                            const event = new Event('change', { bubbles: true });
                            responseElement.dispatchEvent(event);
                        }
                    }
                """, token)

                logger.info("hcaptcha_token_applied")

        except Exception as e:
            logger.error("hcaptcha_solve_failed", error=str(e))
            raise

    async def _solve_image_captcha(self, page: Page, image_element) -> None:
        """Решает image captcha."""
        try:
            # Получаем изображение капчи
            screenshot = await image_element.screenshot()
            image_base64 = base64.b64encode(screenshot).decode('utf-8')

            logger.info("solving_image_captcha")

            # Решаем капчу
            solution = await self.captcha_solver.solve_image_captcha_base64(image_base64)
            logger.info("image_captcha_solved", solution=solution)

            # Находим поле для ввода решения
            input_field = await page.query_selector('input[name="captcha"], input[type="text"]')
            if input_field:
                await input_field.fill(solution)
                logger.info("image_captcha_solution_applied")

        except Exception as e:
            logger.error("image_captcha_solve_failed", error=str(e))
            raise


__all__ = ["BrowserRunner"]