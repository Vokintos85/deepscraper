import asyncio
import os
import sys
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, 'src')

# Правильная загрузка .env файла
def load_env():
    env_path = Path('.env')
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# Загружаем переменные
load_env()

from deepscraper.planner.deepseek_client import DeepSeekClient

async def main():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    print(f"🔑 API ключ из .env: {api_key}")
    
    if not api_key:
        print("❌ API ключ не найден в переменных окружения!")
        return
    
    if api_key == "your_actual_api_key_here":
        print("❌ API ключ установлен как заглушка!")
        return
    
    print(f"✅ API ключ: Установлен ({api_key[:10]}...)")
    
    client = DeepSeekClient()
    
    print("\\n🧪 Тестируем DeepSeek AI...")
    print("📍 URL: https://httpbin.org/html")
    print("🎯 Цель: Извлечь заголовок H1 и основной текст")
    
    try:
        plan = await client.generate_plan(
            url="https://httpbin.org/html",
            goal="Извлечь заголовок H1 и все параграфы текста"
        )
        
        print("\\n✅ УСПЕХ! DeepSeek AI сгенерировал план!")
        print(f"📋 Шагов: {len(plan.steps)}")
        print(f"📊 Полей для извлечения: {[f.name for f in plan.fields]}")
        
        # Сохраняем план
        import json
        with open("deepseek_real_plan.json", "w") as f:
            f.write(plan.model_dump_json(indent=2))
        print("💾 План сохранен в: deepseek_real_plan.json")
        
        # Детали плана
        print("\\n📝 Детали плана:")
        for i, step in enumerate(plan.steps):
            wait_info = f" (wait: {step.wait.type})" if step.wait else ""
            print(f"  {i+1}. {step.action}: {step.target or ''}{wait_info}")
            
    except Exception as e:
        print(f"\\n❌ Ошибка DeepSeek API: {e}")
        import traceback
        traceback.print_exc()
    
    await client.aclose()

asyncio.run(main())
