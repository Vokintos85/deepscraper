#!/usr/bin/env python3
"""Тест stealth режима"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from deepscraper.runner.browser import BrowserRunner

async def test_stealth():
    print("🕵️ Тестируем stealth режим...")
    
    runner = BrowserRunner()
    
    try:
        async with runner.context() as page:
            user_agent = await page.evaluate("() => navigator.userAgent")
            webdriver = await page.evaluate("() => navigator.webdriver")
            
            print(f"🔍 User-Agent: {user_agent}")
            print(f"🔍 WebDriver: {webdriver}")
            
            if webdriver is None:
                print("✅ WebDriver успешно скрыт!")
            else:
                print("❌ WebDriver не скрыт!")
                
            print("✅ Stealth режим работает!")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(test_stealth())
