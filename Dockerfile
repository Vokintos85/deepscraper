FROM python:3.11-slim

ENV POETRY_VERSION=1.7.1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app
COPY pyproject.toml README.md /app/
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --only main

COPY . /app
RUN playwright install --with-deps chromium

CMD ["poetry", "run", "deepscraper", "report"]
