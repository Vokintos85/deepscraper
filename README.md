# DeepScraper - Универсальная платформа для веб-скрапинга с ИИ

**DeepScraper** - это мощная AI-платформа для сбора данных, сочетающая браузерную автоматизацию на **Playwright** с интеллектуальным планированием через **DeepSeek API**.

## Возможности

-  **AI-планирование** - генерация стратегий парсинга через DeepSeek API
-  **Браузерная автоматизация** - Playwright с поддержкой SPA, stealth-режимом
-  **Обход защиты** - stealth-техники, решение капч, смена User-Agent
-  **Капча-сервисы** - интеграция с 2Captcha для reCAPTCHA, hCaptcha
-  **Сохранение данных** - PostgreSQL, Redis, MinIO
-  **Экспорт** - поддержка CSV, Excel, JSON
-  **Продолжение работы** - возобновление прерванных сессий

## Быстрый старт

### Требования
- Python 3.11+
- Poetry для управления зависимостями
- Docker и docker-compose
- DeepSeek API ключ (https://platform.deepseek.com/api_keys)

### Установка

1. **Установите зависимости:**
```bash
poetry install
poetry run playwright install
```

2. **Настройте окружение:**
```bash
cp .env.example .env
# Отредактируйте .env - добавьте API ключи
```

3. **Запустите сервисы:**
```bash
docker compose up -d postgres redis minio
```

## Использование

1. **Создайте план парсинга:**
```bash
poetry run deepscraper plan \
  --url "https://example.com/products" \
  --goal "Собрать названия, цены и артикулы товаров" \
  --out plan.json
```

2. **Запустите парсинг:**
```bash
poetry run deepscraper parse \
  --plan plan.json \
  --project example-products \
  --limit 200 \
  --export csv
```

## Архитектура

- **Core:** Python 3.11, Playwright, AsyncIO
- **AI Layer:** DeepSeek API (LLM-планирование)
- **Storage:** PostgreSQL, Redis, MinIO
- **Exports:** CSV, Excel, JSON

