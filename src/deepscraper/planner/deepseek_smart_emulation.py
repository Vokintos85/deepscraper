import os
import re
from typing import Optional
from .schema import PlanDocument, PlanStep, ExtractionField, PaginationInstruction, WaitInstruction

class DeepSeekClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.has_balance = False  # Предположим, что баланса нет

    async def generate_plan(self, url: str, goal: str) -> PlanDocument:
        print("🤖 Using SMART AI EMULATION (no API balance)")
        
        # Умная эмуляция на основе URL и цели
        return self._smart_ai_emulation(url, goal)

    def _smart_ai_emulation(self, url: str, goal: str) -> PlanDocument:
        """Умная эмуляция AI, которая анализирует цель и URL"""
        
        goal_lower = goal.lower()
        url_lower = url.lower()
        
        # Определяем тип контента по цели
        if any(word in goal_lower for word in ['product', 'price', 'товар', 'цена', 'магазин']):
            return self._ecommerce_plan(url, goal)
        elif any(word in goal_lower for word in ['news', 'article', 'новость', 'статья']):
            return self._news_plan(url, goal)
        elif any(word in goal_lower for word in ['contact', 'email', 'контакт', 'почта']):
            return self._contact_plan(url, goal)
        elif 'json' in url_lower or 'api' in url_lower:
            return self._api_plan(url, goal)
        else:
            return self._generic_plan(url, goal)

    def _ecommerce_plan(self, url: str, goal: str) -> PlanDocument:
        print("🎯 Detected: E-commerce website")
        return PlanDocument(
            url=url,
            goal=goal,
            steps=[
                PlanStep(action="navigate", target=url),
                PlanStep(action="wait", wait=WaitInstruction(type="network_idle", timeout_ms=5000)),
                PlanStep(action="extract", target="products")
            ],
            fields=[
                ExtractionField(name="name", selector=".product-name, h1, [data-product-name], .title", required=True),
                ExtractionField(name="price", selector=".price, .cost, [data-price], .amount", required=True),
                ExtractionField(name="description", selector=".description, .product-desc, .details", required=False),
                ExtractionField(name="image", selector=".product-image img, .thumbnail img", attr="src", required=False),
                ExtractionField(name="sku", selector=".sku, [data-sku], .product-code", required=False)
            ],
            pagination=PaginationInstruction(type="scroll", max_pages=5)
        )

    def _news_plan(self, url: str, goal: str) -> PlanDocument:
        print("🎯 Detected: News/Article website")
        return PlanDocument(
            url=url,
            goal=goal,
            steps=[
                PlanStep(action="navigate", target=url),
                PlanStep(action="wait", wait=WaitInstruction(type="network_idle", timeout_ms=4000)),
                PlanStep(action="extract", target="article")
            ],
            fields=[
                ExtractionField(name="title", selector="h1, .article-title, .headline", required=True),
                ExtractionField(name="content", selector="article, .content, .article-body, p", required=True),
                ExtractionField(name="author", selector=".author, .byline, [rel=author]", required=False),
                ExtractionField(name="date", selector=".date, .publish-date, time", required=False),
                ExtractionField(name="category", selector=".category, .section, .tag", required=False)
            ],
            pagination=PaginationInstruction(type="next_page", selector=".next-page, .pagination-next", max_pages=3)
        )

    def _generic_plan(self, url: str, goal: str) -> PlanDocument:
        print("🎯 Detected: Generic website")
        return PlanDocument(
            url=url,
            goal=goal,
            steps=[
                PlanStep(action="navigate", target=url),
                PlanStep(action="wait", wait=WaitInstruction(type="network_idle", timeout_ms=4000)),
                PlanStep(action="extract", target="main-content")
            ],
            fields=[
                ExtractionField(name="title", selector="h1, .title, [role=heading]", required=True),
                ExtractionField(name="content", selector="main, article, .content, p", required=True),
                ExtractionField(name="subtitle", selector="h2, h3, .subtitle", required=False),
                ExtractionField(name="links", selector="a", attr="href", required=False)
            ],
            pagination=PaginationInstruction(type="none", max_pages=1)
        )

    def _contact_plan(self, url: str, goal: str) -> PlanDocument:
        print("🎯 Detected: Contact information")
        return PlanDocument(
            url=url,
            goal=goal,
            steps=[
                PlanStep(action="navigate", target=url),
                PlanStep(action="wait", wait=WaitInstruction(type="network_idle", timeout_ms=3000)),
                PlanStep(action="extract", target="contacts")
            ],
            fields=[
                ExtractionField(name="email", selector="a[href^='mailto:'], [href*='mailto']", attr="href", required=False),
                ExtractionField(name="phone", selector="a[href^='tel:'], [href*='tel:']", attr="href", required=False),
                ExtractionField(name="address", selector=".address, [itemprop=address]", required=False),
                ExtractionField(name="contact_name", selector=".contact-name, .person", required=False)
            ],
            pagination=PaginationInstruction(type="none", max_pages=1)
        )

    def _api_plan(self, url: str, goal: str) -> PlanDocument:
        print("🎯 Detected: API/JSON endpoint")
        return PlanDocument(
            url=url,
            goal=goal,
            steps=[
                PlanStep(action="navigate", target=url),
                PlanStep(action="wait", wait=WaitInstruction(type="network_idle", timeout_ms=2000)),
                PlanStep(action="extract", target="json-content")
            ],
            fields=[
                ExtractionField(name="json_data", selector="pre, body", required=True),
            ],
            pagination=PaginationInstruction(type="none", max_pages=1)
        )

    async def aclose(self):
        pass

