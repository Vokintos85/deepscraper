import asyncio
import os
import sys
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

async def test_complex_scenarios():
    client = DeepSeekClient()
    
    scenarios = [
        {
            "url": "https://example.com/products", 
            "goal": "Собрать названия товаров, цены, описания и изображения с поддержкой пагинации"
        },
        {
            "url": "https://news-site.com/articles",
            "goal": "Извлечь заголовки статей, даты публикации, авторов и краткое содержание"
        },
        {
            "url": "https://company.com/about", 
            "goal": "Найти контактные данные: email, телефоны, адреса и социальные сети"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\\n🧪 Сценарий {i}: {scenario['goal']}")
        print(f"📍 URL: {scenario['url']}")
        
        try:
            plan = await client.generate_plan(scenario['url'], scenario['goal'])
            print(f"✅ AI сгенерировал план: {len(plan.fields)} полей")
            print(f"📊 Поля: {[f.name for f in plan.fields]}")
            print(f"🔄 Пагинация: {plan.pagination.type}")
            
            # Сохраняем отдельные планы
            with open(f"ai_plan_scenario_{i}.json", "w") as f:
                f.write(plan.model_dump_json(indent=2))
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    await client.aclose()
    print("\\n🎉 Все сценарии протестированы!")

asyncio.run(test_complex_scenarios())
