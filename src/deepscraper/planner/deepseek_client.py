import os
import aiohttp
from typing import Optional
from .schema import PlanDocument, PlanStep, ExtractionField, PaginationInstruction, WaitInstruction

class DeepSeekClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.base_url = "https://api.deepseek.com/v1"
        self.session: Optional[aiohttp.ClientSession] = None

    async def _ensure_session(self):
        if not self.session:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self.session = aiohttp.ClientSession(headers=headers)

    async def generate_plan(self, url: str, goal: str) -> PlanDocument:
        await self._ensure_session()
        
        # Если нет API ключа, используем эвристический план
        if not self.api_key:
            print("⚠️  No DEEPSEEK_API_KEY, using heuristic plan")
            return self._heuristic_plan(url, goal)
        
        try:
            # Пробуем использовать API
            prompt = f"""
            Create a web scraping plan for: {url}
            Goal: {goal}
            
            Return structured scraping instructions.
            """
            
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "You are a web scraping expert."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    # Парсим ответ или используем эвристический план
                    return self._heuristic_plan(url, goal)
                else:
                    return self._heuristic_plan(url, goal)
                    
        except Exception as e:
            print(f"⚠️  API error: {e}, using heuristic plan")
            return self._heuristic_plan(url, goal)

    def _heuristic_plan(self, url: str, goal: str) -> PlanDocument:
        return PlanDocument(
            url=url,
            goal=goal,
            steps=[
                PlanStep(action="navigate", target=url),
                PlanStep(action="wait", wait=WaitInstruction(type="network_idle", timeout_ms=5000)),
                PlanStep(action="extract", target="content")
            ],
            fields=[
                ExtractionField(name="title", selector="h1, h2, .title, [data-title]"),
                ExtractionField(name="content", selector="p, .content, .text, article"),
                ExtractionField(name="price", selector=".price, [data-price], .cost"),
                ExtractionField(name="description", selector=".description, .desc, [data-desc]")
            ],
            pagination=PaginationInstruction(type="none", max_pages=1)
        )

    async def aclose(self):
        if self.session:
            await self.session.close()
