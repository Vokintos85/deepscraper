"""Typer-based CLI entrypoint."""
from __future__ import annotations

import asyncio
from itertools import zip_longest
from pathlib import Path
from typing import List

import typer
from sqlalchemy import select

from .config import get_settings
from .exporters.csv_exporter import export_to_csv
from .exporters.excel_exporter import export_to_excel
from .exporters.json_exporter import export_to_json
from .logging import configure_logging, get_logger
from .pipeline.db import init_db, session_scope
from .pipeline.models import Item, Project, Run
from .planner.deepseek_client import DeepSeekClient
from .planner.schema import PlanDocument
from .proxy.manager import ProxyManager
from .runner.browser import BrowserRunner

app = typer.Typer(help="AI-assisted universal scraping platform")
logger = get_logger(__name__)


async def _ensure_project(session, name: str) -> Project:
    result = await session.execute(select(Project).where(Project.name == name))
    project_obj = result.scalar_one_or_none()
    if project_obj:
        return project_obj
    project = Project(name=name)
    session.add(project)
    await session.flush()
    return project


async def _create_run(session, project: Project, plan: PlanDocument) -> Run:
    run = Run(project_id=project.id, plan=plan.model_dump())
    session.add(run)
    await session.flush()
    return run


async def _execute_plan(plan: PlanDocument, limit: int) -> List[dict]:
    settings = get_settings()
    proxy_manager = ProxyManager(settings.proxy_list) if settings.proxy_list else None
    runner = BrowserRunner(proxy_manager)
    extracted_rows: List[dict] = []
    async with runner.context() as page:
        for step in plan.steps:
            if step.action == "navigate" and step.target:
                await runner.navigate(page, step.target)
            elif step.action == "click" and step.target:
                await page.click(step.target)
            elif step.action == "fill" and step.target and step.value is not None:
                await page.fill(step.target, step.value)
            elif step.action == "wait" and step.wait:
                await runner.wait(page, step.wait.model_dump())
            elif step.action == "extract":
                extracted = await runner.extract_fields(page, [field.model_dump() for field in plan.fields])
                field_names = [field["name"] for field in extracted]
                field_values = [field["values"] for field in extracted]
                for row_values in zip_longest(*field_values, fillvalue=""):
                    item = {name: value for name, value in zip(field_names, row_values)}
                    extracted_rows.append(item)
                    if len(extracted_rows) >= limit:
                        break
            if len(extracted_rows) >= limit:
                break
        if plan.pagination.type != "none":
            await runner.paginate(page, plan.pagination.model_dump())
    return extracted_rows[:limit]


def _export(rows: List[dict], export: str, project: str) -> Path:
    filename = f"{project}." + ("csv" if export == "csv" else "json" if export == "json" else "xlsx")
    if export == "csv":
        return export_to_csv(rows, filename)
    if export == "excel":
        return export_to_excel(rows, filename)
    return export_to_json(rows, filename)


@app.command()
def plan(
    url: str,
    goal: str,
    out: Path = Path("plan.json")
):
    """Generate a scraping plan for the target URL and goal."""

    configure_logging(get_settings().log_level)

    async def _plan() -> None:
        client = DeepSeekClient()
        plan_doc = await client.generate_plan(url=url, goal=goal)
        out.write_text(plan_doc.model_dump_json(indent=2), encoding="utf-8")
        await client.aclose()
        logger.info("plan_created", path=str(out))

    asyncio.run(_plan())


@app.command()
def parse(
    plan: Path = typer.Option(..., help="Path to plan JSON file"),
    project: str = typer.Option(..., help="Project name"),
    limit: int = typer.Option(100, help="Maximum items to extract"),
    export: str = typer.Option("json", help="Export format: csv|excel|json")
):
    """Execute a scraping plan and persist the results."""

    configure_logging(get_settings().log_level)

    async def _parse() -> None:
        await init_db()
        plan_doc = PlanDocument.model_validate_json(plan.read_text())
        async with session_scope() as session:
            project_obj = await _ensure_project(session, project)
            run = await _create_run(session, project_obj, plan_doc)
            rows = await _execute_plan(plan_doc, limit)
            for row in rows:
                session.add(Item(run_id=run.id, data=row))
        export_path = _export(rows, export, project)
        logger.info("parse_complete", items=len(rows), export=str(export_path))

    asyncio.run(_parse())


@app.command()
def resume(project: str = typer.Option(..., help="Project name to resume")):
    """Resume the latest incomplete run for a project."""

    configure_logging(get_settings().log_level)

    async def _resume() -> None:
        async with session_scope() as session:
            result = await session.execute(
                select(Run)
                .join(Project, Run.project_id == Project.id)
                .where(Project.name == project, Run.status != "completed")
                .order_by(Run.created_at.desc())
                .limit(1)
            )
            run = result.scalar_one_or_none()
            if not run:
                logger.info("no_pending_runs", project=project)
                return
            plan_doc = PlanDocument.model_validate(run.plan)
            rows = await _execute_plan(plan_doc, limit=100)
            for item in rows:
                session.add(Item(run_id=run.id, data=item))
            run.status = "completed"
        logger.info("resume_complete", project=project)

    asyncio.run(_resume())


@app.command()
def report(project: str = typer.Option(..., help="Project name to report on")):
    """Display a summary of recent runs."""

    configure_logging(get_settings().log_level)

    async def _report() -> None:
        async with session_scope() as session:
            result = await session.execute(
                select(Run)
                .join(Project, Run.project_id == Project.id)
                .where(Project.name == project)
                .order_by(Run.created_at.desc())
                .limit(5)
            )
            runs = result.scalars().all()
            if not runs:
                typer.echo("No runs recorded yet.")
                return
            for run in runs:
                typer.echo(f"Run {run.id}: status={run.status} created_at={run.created_at}")

    asyncio.run(_report())


if __name__ == "__main__":
    app()

__all__ = ["app", "plan", "parse", "resume", "report"]
