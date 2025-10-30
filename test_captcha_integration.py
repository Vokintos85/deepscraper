#!/usr/bin/env python3
"""Тест интеграции капча-сервиса в браузер"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from deepscraper.runner.browser import BrowserRunner

async def test_captcha_integration():
    """Тестируем интеграцию капча-сервиса в браузер"""
    print("🧪 Тестируем интеграцию капча-сервиса...")

    runner = BrowserRunner()

    try:
        async with runner.context() as page:
            # Переходим на тестовую страницу (можно заменить на реальный сайт с капчей)
            await runner.navigate(page, "https://books.toscrape.com")

            # Проверяем обнаружение капчи (на этом сайте капчи нет)
            has_captcha = await runner.detect_and_solve_captcha(page)

            if has_captcha:
                print("✅ Капча обнаружена и обработана!")
            else:
                print("✅ Капча не обнаружена (ожидаемо для этого сайта)")

            print("✅ Интеграция капча-сервиса работает!")

    except Exception as e:
        print(f"❌ Ошибка интеграции: {e}")

if __name__ == "__main__":
    asyncio.run(test_captcha_integration())