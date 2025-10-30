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

async def main():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    print(f"🔑 Новый API ключ: {api_key[:10]}...")
    
    client = DeepSeekClient()
    
    print("\\n🧪 Тестируем РЕАЛЬНЫЙ DeepSeek AI с новым токеном...")
    
    try:
        plan = await client.generate_plan(
            url="https://httpbin.org/html",
            goal="Извлечь заголовок H1 и основной текст страницы"
        )
        
        print("\\n✅ РЕАЛЬНЫЙ AI СГЕНЕРИРОВАЛ ПЛАН!")
        print(f"📋 Шагов: {len(plan.steps)}")
        print(f"📊 Полей: {[f.name for f in plan.fields]}")
        print(f"🎯 Селекторы: {[f.selector for f in plan.fields]}")
        
        # Сохраняем результат реального AI
        with open("real_ai_plan.json", "w") as f:
            f.write(plan.model_dump_json(indent=2))
        print("💾 План сохранен в: real_ai_plan.json")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    await client.aclose()

asyncio.run(main())
