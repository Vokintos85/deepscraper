You are generating a production-ready Python 3.11 project called "deepscraper":
an AI-assisted universal scraping platform that works on SPA sites with filters,
uses Playwright for browser automation, integrates DeepSeek API for planning selectors/steps,
supports proxy rotation, captcha solving services, resumable jobs, and exports to CSV/Excel/JSON.

## Goals
- CLI-first MVP with clean architecture and strong typing.
- Runner executes LLM-generated plans (selectors, waits, pagination, filters).
- SPA support: intercept XHR/GraphQL, wait for network idle, handle infinite scroll.
- Anti-bot hygiene: randomized headers, cookie jar, proxy pool, throttling.
- Captcha abstraction: 2Captcha/CapSolver via adapter interface.
- Schema-first extraction: validate fields with Pydantic v2, deduplicate, normalize.
- Persistence: Postgres for results/meta, Redis for queues, MinIO (S3) for HTML/snapshots.
- Exporters: CSV/Excel/JSON per task.
- Observability: structured logging, basic metrics, run reports.

## Tech constraints
- Python 3.11+, Playwright (default) + stealth, optional Selenium profile.
- FastAPI minimal stub for future Web-UI, but main is CLI.
- Pydantic v2, SQLAlchemy 2.x, Alembic migrations.
- Redis (RQ/Celery-like queue; pick one and wire), Postgres, MinIO/S3.
- Lint/format/type: Ruff, Black, isort, mypy; pre-commit hooks.
- Tests: pytest with a couple of integration-like stubs (mock browser).
- Docker + docker-compose with services (postgres, redis, minio, app).
- Makefile for common tasks.

## Deliverables (files to produce)
- README.md (clear quickstart).
- .env.example with all required vars.
- pyproject.toml (poetry) OR requirements.txt + uv/pip-tools (choose and be consistent).
- docker-compose.yml and Dockerfile.
- Makefile with targets: install, lint, fmt, type, test, up, down, parse, report, migrate.
- src/ structure:
  - src/deepscraper/__init__.py
  - src/deepscraper/config.py (pydantic settings)
  - src/deepscraper/logging.py (structured/simple logger)
  - src/deepscraper/proxy/manager.py (load/rotate proxies, backoff)
  - src/deepscraper/captcha/base.py (interface), src/deepscraper/captcha/{twocaptcha,capsolver}.py
  - src/deepscraper/planner/deepseek_client.py (simple SDK), planner/schema.py
  - src/deepscraper/runner/browser.py (Playwright controller, stealth, waits, XHR capture stub)
  - src/deepscraper/extractor/{dom.py, network.py, llm_fallback.py}
  - src/deepscraper/pipeline/{models.py, db.py} + migrations/
  - src/deepscraper/exporters/{csv_exporter.py, excel_exporter.py, json_exporter.py}
  - src/deepscraper/tasks/queue.py (Redis worker + retry policy)
  - src/deepscraper/utils/{randomize.py, timing.py, snapshots.py}
  - src/deepscraper/cli.py (typer) with commands: plan, parse, resume, report
  - src/deepscraper/web/api.py (FastAPI stub + /healthz)

## CLI contract
- `deepscraper plan --url <start_url> --goal "<natural language>" --out plan.json`
- `deepscraper parse --plan plan.json --project mysite --limit 200 --export csv|excel|json`
- `deepscraper resume --project mysite`
- `deepscraper report --project mysite`

## DeepSeek integration
- Read base_url + API key from env; minimal client wrapper.
- Planner input: page DOM snapshot hint + user goal.
- Output JSON schema (pydantic): steps[], selectors[], waits[], fields[], pagination.
- Fallback: if no API key, return a sane heuristic plan.

## Anti-bot hygiene
- Random UA, viewport, jittered timeouts, human-like delays.
- Proxy rotation with per-domain stickiness; rate-limits.
- Cookie jar persisted per project; session warm-up.

## Captcha
- Unified interface: solve(image|sitekey, url, type) -> token/text.
- Adapters: 2Captcha, CapSolver (stubs with TODOs ok for MVP).

## Persistence
- Postgres tables: projects, runs, pages, items (jsonb), failures, checkpoints.
- Alembic migration initial script (or init_db fallback).

## Exports
- exporters write to ./exports/, filenames with ISO timestamp.

## Observability
- JSON-ish logs; run summary: pages, items, bans, captcha attempts, spend (placeholder).

## Testing targets
- unit: planner schema, exporters, proxy manager.
- integration-like: local HTML fixtures (no live scraping).

## .env.example keys
DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
POSTGRES_DSN=postgresql+psycopg://deepscraper:deepscraper@localhost:5432/deepscraper
REDIS_URL=redis://localhost:6379/0
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=deepscraper
MINIO_SECRET_KEY=deepscrapersecret
MINIO_BUCKET=deepscraper
MINIO_SECURE=false
PROXY_LIST_PATH=./proxies.txt
PLAYWRIGHT_STEALTH=1
CAPTCHA_PROVIDER=twocaptcha
CAPTCHA_API_KEY=
HEADLESS=1
LOG_LEVEL=INFO

## README Quickstart (must include)
- venv + install; playwright install.
- docker-compose up -d postgres redis minio
- create bucket for minio
- run: `deepscraper plan ...` then `deepscraper parse ...`
- troubleshooting tips (timeouts, proxies, captchas)

## Code quality
- Type-hint everything, mypy clean (or TODO for strict).
- Ruff + Black + isort + pre-commit.
- Small functions, no god-objects.

Output the FULL project tree and ALL files with real code. Do not handwave or omit files.
