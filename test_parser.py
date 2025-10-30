#!/usr/bin/env python3
"""Простой тест AI-парсера"""

import asyncio
import json
from pathlib import Path

# Добавляем src в путь импорта
import sys
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from deepscraper.planner.deepseek_client import DeepSeekClient
from deepscraper.runner.browser import BrowserRunner
from deepscraper.config import get_settings

async def test_plan_generation():
    """Тест генерации плана"""
    print("🧠 Тестируем генерацию AI-плана...")
    
    client = DeepSeekClient()
    try:
        plan = await client.generate_plan(
            url="https://books.toscrape.com",
            goal="Собрать названия книг и цены"
        )
        
        print("✅ План успешно сгенерирован!")
        print(f"📄 URL: {plan.url}")
        print(f"🎯 Цель: {plan.goal}")
        print(f"📋 Шаги: {len(plan.steps)}")
        print(f"📊 Поля: {[f.name for f in plan.fields]}")
        
        # Сохраняем план для просмотра
        with open("simple_plan.json", "w", encoding="utf-8") as f:
            f.write(plan.model_dump_json(indent=2))
        print("💾 План сохранен в simple_plan.json")
        
    except Exception as e:
        print(f"❌ Ошибка генерации плана: {e}")
    finally:
        await client.aclose()

async def test_browser():
    """Тест браузера"""
    print("\n🌐 Тестируем браузер...")
    
    runner = BrowserRunner()
    try:
        async with runner.context() as page:
            await runner.navigate(page, "https://books.toscrape.com")
            title = await page.title()
            print(f"✅ Браузер работает! Заголовок: {title}")
            
            # Простой тест извлечения данных
            content = await page.content()
            if "books" in content.lower():
                print("✅ Контент страницы загружен корректно")
            else:
                print("⚠️  Контент может быть неполным")
                
    except Exception as e:
        print(f"❌ Ошибка браузера: {e}")

async def main():
    """Основная функция тестирования"""
    print("🚀 Запускаем тест AI-парсера...")
    
    # Проверяем настройки
    settings = get_settings()
    print(f"⚙️  Настройки загружены: POSTGRES_DSN={settings.postgres_dsn}")
    
    # Тестируем генерацию плана
    await test_plan_generation()
    
    # Тестируем браузер
    await test_browser()
    
    print("\n🎉 Тестирование завершено!")

if __name__ == "__main__":
    asyncio.run(main())
