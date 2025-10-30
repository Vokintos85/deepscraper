import os
import aiohttp
import json
import re
from typing import Optional
from .schema import PlanDocument, PlanStep, ExtractionField, PaginationInstruction, WaitInstruction

class DeepSeekClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.base_url = "https://api.deepseek.com/v1"
        self.session: Optional[aiohttp.ClientSession] = None

    async def _ensure_session(self):
        if not self.session and self.api_key:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            self.session = aiohttp.ClientSession(headers=headers)

    async def generate_plan(self, url: str, goal: str) -> PlanDocument:
        await self._ensure_session()
        
        if not self.api_key:
            print("⚠️  No API key, using heuristic plan")
            return self._heuristic_plan(url, goal)
        
        try:
            print("🤖 Calling REAL DeepSeek API...")
            
            prompt = f"""
            Create a detailed web scraping plan in JSON format.

            URL: {url}
            Goal: {goal}

            Return ONLY valid JSON with this structure:
            {{
                "steps": [
                    {{"action": "navigate", "target": "url"}},
                    {{"action": "wait", "wait": {{"type": "network_idle", "timeout_ms": 5000}}}},
                    {{"action": "extract", "target": "description"}}
                ],
                "fields": [
                    {{"name": "title", "selector": "h1, .title", "required": true}},
                    {{"name": "content", "selector": "p, .content", "required": true}}
                ],
                "pagination": {{"type": "none", "max_pages": 1}}
            }}

            Provide practical CSS selectors that work on real websites.
            Focus on the specific goal: {goal}
            """
            
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {
                            "role": "system", 
                            "content": "You are a web scraping expert. Always return valid JSON. Use practical CSS selectors."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    "temperature": 0.1,
                    "max_tokens": 2000,
                    "response_format": {"type": "json_object"}
                },
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    ai_response = data["choices"][0]["message"]["content"]
                    print(f"✅ DeepSeek AI Response received ({len(ai_response)} chars)")
                    
                    # Извлекаем JSON из ответа
                    json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                    if json_match:
                        try:
                            plan_data = json.loads(json_match.group())
                            print("🎯 Successfully parsed AI JSON response!")
                            return self._parse_ai_response(plan_data, url, goal)
                        except json.JSONDecodeError as e:
                            print(f"❌ Failed to parse AI JSON: {e}")
                    
                    print("❌ No valid JSON in AI response, using heuristic")
                    return self._heuristic_plan(url, goal)
                    
                else:
                    error_text = await response.text()
                    print(f"❌ API error {response.status}: {error_text}")
                    return self._heuristic_plan(url, goal)
                    
        except Exception as e:
            print(f"❌ API call failed: {e}")
            return self._heuristic_plan(url, goal)

    def _parse_ai_response(self, plan_data: dict, url: str, goal: str) -> PlanDocument:
        """Парсит JSON ответ от AI в PlanDocument"""
        try:
            # Шаги
            steps = []
            for step_data in plan_data.get("steps", []):
                wait_data = step_data.get("wait", {})
                wait_instruction = WaitInstruction(**wait_data) if wait_data else None
                
                steps.append(PlanStep(
                    action=step_data["action"],
                    target=step_data.get("target"),
                    value=step_data.get("value"),
                    wait=wait_instruction
                ))

            # Поля для извлечения
            fields = []
            for field_data in plan_data.get("fields", []):
                fields.append(ExtractionField(
                    name=field_data["name"],
                    selector=field_data["selector"],
                    attr=field_data.get("attr"),
                    required=field_data.get("required", False)
                ))

            # Пагинация
            pagination_data = plan_data.get("pagination", {})
            pagination = PaginationInstruction(
                type=pagination_data.get("type", "none"),
                selector=pagination_data.get("selector"),
                max_pages=pagination_data.get("max_pages", 1)
            )

            return PlanDocument(
                url=url,
                goal=goal,
                steps=steps,
                fields=fields,
                pagination=pagination
            )
            
        except Exception as e:
            print(f"❌ Error parsing AI plan: {e}")
            return self._heuristic_plan(url, goal)

    def _heuristic_plan(self, url: str, goal: str) -> PlanDocument:
        """Fallback план"""
        return PlanDocument(
            url=url,
            goal=goal,
            steps=[
                PlanStep(action="navigate", target=url),
                PlanStep(action="wait", wait=WaitInstruction(type="network_idle", timeout_ms=5000)),
                PlanStep(action="extract", target="content")
            ],
            fields=[
                ExtractionField(name="title", selector="h1, .title", required=True),
                ExtractionField(name="content", selector="p, .content", required=True)
            ],
            pagination=PaginationInstruction(type="none", max_pages=1)
        )

    async def aclose(self):
        if self.session:
            await self.session.close()
