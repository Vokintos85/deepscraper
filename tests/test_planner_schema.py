from __future__ import annotations

from deepscraper.planner.schema import PlanDocument, PlanStep, ExtractionField


def test_plan_document_validation() -> None:
    plan = PlanDocument(
        url="https://example.com",
        goal="Collect items",
        steps=[PlanStep(action="navigate", target="https://example.com")],
        fields=[ExtractionField(name="title", selector="h1")],
    )
    assert plan.url == "https://example.com"
