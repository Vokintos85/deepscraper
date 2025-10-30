import asyncio
import os
import sys
sys.path.insert(0, 'src')

from deepscraper.planner.deepseek_client import DeepSeekClient

async def main():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    print(f"🔑 API ключ: ✅ Установлен ({api_key[:10]}...)")
    
    client = DeepSeekClient()
    
    print("\\n🧪 Тестируем реальный DeepSeek AI...")
    print("📍 URL: https://httpbin.org/html")
    print("🎯 Цель: Извлечь заголовок H1 и основной текст")
    
    try:
        plan = await client.generate_plan(
            url="https://httpbin.org/html",
            goal="Извлечь заголовок H1 и все параграфы текста"
        )
        
        print("\\n✅ УСПЕХ! DeepSeek AI сгенерировал план:")
        print(f"📋 Шагов: {len(plan.steps)}")
        print(f"📊 Полей для извлечения: {[f.name for f in plan.fields]}")
        
        # Сохраним план для проверки
        import json
        with open("deepseek_ai_plan.json", "w") as f:
            f.write(plan.model_dump_json(indent=2))
        print("💾 План сохранен в: deepseek_ai_plan.json")
        
        # Покажем детали плана
        print("\\n📝 Детали плана:")
        for i, step in enumerate(plan.steps):
            print(f"  {i+1}. {step.action}: {step.target or ''}")
        
    except Exception as e:
        print(f"\\n❌ Ошибка DeepSeek API: {e}")
        print("🔧 Возможные причины:")
        print("   - Неправильный API ключ")
        print("   - Нет доступа к api.deepseek.com") 
        print("   - Закончились средства на аккаунте")
        print("   - Проблемы с сетью")
    
    await client.aclose()

asyncio.run(main())
