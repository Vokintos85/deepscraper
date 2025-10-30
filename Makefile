.PHONY: install fmt lint type test up down parse plan resume report worker

install:
	poetry install
	poetry run playwright install

fmt:
	poetry run black src tests
	poetry run isort src tests

lint:
	poetry run ruff check src tests

type:
	poetry run mypy src

test:
	poetry run pytest

up:
	docker compose up -d postgres redis minio

down:
	docker compose down

plan:
	poetry run deepscraper plan --url "$(url)" --goal "$(goal)" --out "$(out)"

parse:
	poetry run deepscraper parse --plan "$(plan)" --project "$(project)" --limit $(limit) --export $(export)

resume:
	poetry run deepscraper resume --project "$(project)"

report:
	poetry run deepscraper report --project "$(project)"

worker:
	poetry run deepscraper-worker
