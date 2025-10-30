#!/usr/bin/env python3
"""Полный тест парсинга с извлечением данных"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from deepscraper.planner.deepseek_client import DeepSeekClient
from deepscraper.runner.browser import BrowserRunner
from deepscraper.config import get_settings

async def test_full_parsing():
    """Полный тест парсинга с извлечением данных"""
    print("🚀 Запускаем полный тест парсинга...")
    
    # Генерируем план
    client = DeepSeekClient()
    plan = await client.generate_plan(
        url="https://books.toscrape.com",
        goal="Собрать названия книг и цены"
    )
    await client.aclose()
    
    print(f"📋 Используем план с {len(plan.steps)} шагами")
    
    # Запускаем парсинг
    runner = BrowserRunner()
    extracted_data = []
    
    try:
        async with runner.context() as page:
            for step in plan.steps:
                if step.action == "navigate" and step.target:
                    print(f"🌐 Переходим на: {step.target}")
                    await runner.navigate(page, step.target)
                    
                elif step.action == "wait" and step.wait:
                    print("⏳ Ожидаем загрузку...")
                    await runner.wait(page, step.wait.model_dump())
                    
                elif step.action == "extract":
                    print("📊 Извлекаем данные...")
                    # Извлекаем данные по полям из плана
                    for field in plan.fields:
                        selector = field.selector
                        try:
                            elements = await page.query_selector_all(selector)
                            values = []
                            for element in elements[:5]:  # Ограничиваем первыми 5 элементами
                                text = await element.text_content()
                                if text:
                                    values.append(text.strip())
                            
                            print(f"  📝 {field.name}: {len(values)} значений")
                            for i, value in enumerate(values[:3]):  # Показываем первые 3
                                print(f"    {i+1}. {value}")
                                
                        except Exception as e:
                            print(f"  ❌ Ошибка извлечения {field.name}: {e}")
            
            # Делаем скриншот для проверки
            await page.screenshot(path="test_screenshot.png")
            print("📸 Скриншот сохранен в test_screenshot.png")
            
    except Exception as e:
        print(f"❌ Ошибка парсинга: {e}")
    
    print("🎉 Парсинг завершен!")

if __name__ == "__main__":
    asyncio.run(test_full_parsing())
