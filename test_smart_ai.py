import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, 'src')

# Загружаем .env
env_path = Path('.env')
if env_path.exists():
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

from deepscraper.planner.deepseek_client import DeepSeekClient

async def test_scenario(url, goal):
    print(f"\\n🎯 Тестируем: {url}")
    print(f"📋 Цель: {goal}")
    
    client = DeepSeekClient()
    plan = await client.generate_plan(url, goal)
    
    print(f"🤖 Определен тип: {len(plan.fields)} полей")
    print(f"📊 Поля: {[f.name for f in plan.fields]}")
    print(f"🔄 Пагинация: {plan.pagination.type}")
    
    await client.aclose()
    return plan

async def main():
    # Разные сценарии
    scenarios = [
        ("https://example-shop.com/products", "Собрать названия и цены товаров"),
        ("https://news-site.com/article", "Извлечь заголовок и текст новости"),
        ("https://company.com/contacts", "Найти email и телефоны"),
        ("https://httpbin.org/json", "Получить JSON данные"),
        ("https://httpbin.org/html", "Извлечь основной контент")
    ]
    
    for url, goal in scenarios:
        await test_scenario(url, goal)

asyncio.run(main())
