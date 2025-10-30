#!/usr/bin/env python3
"""Тест капча-сервисов"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from deepscraper.captcha.base import get_solver
from deepscraper.config import get_settings

async def test_captcha_service():
    """Тестируем капча-сервис"""
    print("🧪 Тестируем капча-сервисы...")
    
    settings = get_settings()
    
    if not settings.captcha_api_key:
        print("⚠️  CAPTCHA_API_KEY не установлен, тестируем NullCaptchaSolver")
        solver = get_solver("twocaptcha", None)
        
        try:
            await solver.get_balance()
        except RuntimeError as e:
            print(f"✅ NullCaptchaSolver работает: {e}")
        
        return
    
    # Тестируем реальный сервис
    solver = get_solver(settings.captcha_provider, settings.captcha_api_key)
    
    try:
        # Проверяем баланс
        balance = await solver.get_balance()
        print(f"💰 Баланс {settings.captcha_provider}: ${balance:.2f}")
        
        if balance < 1.0:
            print("⚠️  Баланс менее $1.0, пополните счет для тестирования")
        else:
            print("✅ Капча-сервис работает корректно!")
            
    except Exception as e:
        print(f"❌ Ошибка капча-сервиса: {e}")
    
    # Закрываем соединение если нужно
    if hasattr(solver, 'aclose'):
        await solver.aclose()

if __name__ == "__main__":
    asyncio.run(test_captcha_service())
