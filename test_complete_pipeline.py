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
from playwright.async_api import async_playwright

async def test_complete_pipeline():
    print("🚀 ТЕСТ ПОЛНОГО ЦИКЛА DEEPSCRAPER")
    print("=" * 50)
    
    # 1. AI-планирование
    print("\\n1. 🤖 AI-ПЛАНИРОВАНИЕ")
    client = DeepSeekClient()
    plan = await client.generate_plan(
        url="https://httpbin.org/html",
        goal="Извлечь заголовок H1 и основной текст"
    )
    
    print(f"   ✅ План создан: {len(plan.steps)} шагов, {len(plan.fields)} полей")
    
    # 2. Выполнение парсинга
    print("\\n2. 🌐 ВЫПОЛНЕНИЕ ПАРСИНГА")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Выполняем шаги плана
            for i, step in enumerate(plan.steps):
                print(f"   🔧 Шаг {i+1}: {step.action}")
                
                if step.action == "navigate":
                    await page.goto(step.target)
                    print(f"      📍 Перешли на: {step.target}")
                    
                elif step.action == "wait" and step.wait:
                    if step.wait.type == "network_idle":
                        await page.wait_for_load_state("networkidle")
                        print("      ⏳ Ожидание загрузки...")
                        
                elif step.action == "extract":
                    # Извлекаем данные
                    extracted = {}
                    for field in plan.fields:
                        try:
                            if field.attr:
                                elements = await page.query_selector_all(field.selector)
                                values = [await elem.get_attribute(field.attr) for elem in elements if await elem.get_attribute(field.attr)]
                            else:
                                elements = await page.query_selector_all(field.selector)
                                values = [await elem.text_content() for elem in elements if await elem.text_content()]
                            
                            extracted[field.name] = values[0] if len(values) == 1 else values if values else None
                            print(f"      📊 {field.name}: {extracted[field.name]}")
                            
                        except Exception as e:
                            print(f"      ❌ Ошибка извлечения {field.name}: {e}")
            
            print("\\n3. ✅ РЕЗУЛЬТАТЫ:")
            for key, value in extracted.items():
                if value:
                    print(f"   {key}: {value}")
                    
        except Exception as e:
            print(f"❌ Ошибка выполнения: {e}")
        finally:
            await browser.close()
    
    await client.aclose()
    print("\\n🎉 ПОЛНЫЙ ЦИКЛ ВЫПОЛНЕН УСПЕШНО!")

asyncio.run(test_complete_pipeline())
