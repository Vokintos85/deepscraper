# Deepscraper

Deepscraper is a CLI-first scraping platform that pairs a Playwright-powered runner with an AI-assisted planning pipeline. It is designed for collecting structured data from modern web applications, including SPAs with dynamic filters and network activity.

## Features
- Plan scraping strategies with the DeepSeek API or a deterministic heuristic fallback.
- Execute browser automation with Playwright, stealth tuning, proxy rotation, and captcha solving hooks.
- Persist run metadata and scraped items into PostgreSQL, with Redis-backed job queues and MinIO for raw assets.
- Export collected data into CSV, Excel, or JSON formats.
- Resume paused runs and generate simple reports from stored metadata.

## Quickstart

### Prerequisites
- Python 3.11+
- [Poetry](https://python-poetry.org/) for dependency management.
- Docker and docker-compose for running the backing services.

### Setup
1. Create a virtual environment and install dependencies:
   ```bash
   poetry install
   poetry run playwright install
   ```

2. Copy the example environment file and update the secrets:
   ```bash
   cp .env.example .env
   ```

3. Start the infrastructure services:
   ```bash
   docker compose up -d postgres redis minio
   ```

4. Create the MinIO bucket listed in `.env` (defaults to `deepscraper`). You can use the MinIO Console at http://localhost:9001 to create it.

5. Generate a plan for a target site:
   ```bash
   poetry run deepscraper plan \
     --url "https://example.com/products" \
     --goal "Collect product names, prices, and SKUs" \
     --out plan.json
   ```

6. Execute the scraping run using the generated plan and export the collected data:
   ```bash
   poetry run deepscraper parse \
     --plan plan.json \
     --project example-products \
     --limit 200 \
     --export csv
   ```

7. Resume a paused run or inspect previous runs:
   ```bash
   poetry run deepscraper resume --project example-products
   poetry run deepscraper report --project example-products
   ```

## Troubleshooting
- **Timeouts or blank pages**: increase the `PAGE_TIMEOUT` setting or use a residential proxy list.
- **Captcha loops**: configure a captcha provider (`CAPTCHA_PROVIDER` and `CAPTCHA_API_KEY`).
- **Proxy bans**: expand the proxy pool and enable sticky sessions in `PROXY_LIST_PATH`.
- **LLM failures**: ensure the DeepSeek API key is set; otherwise the planner falls back to heuristic steps.

## Development
- Run formatting and linting with `make fmt` and `make lint`.
- Execute the test suite with `make test`.
- Use `make up`/`make down` to manage the docker-compose services.

## License
This project is licensed under the terms of the MIT license. See [LICENSE](LICENSE).
