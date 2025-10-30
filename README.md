# DeepScraper — Универсальная платформа для веб-скрапинга с искусственным интеллектом

**DeepScraper** — это мощная AI-платформа для сбора данных, сочетающая браузерную автоматизацию на **Playwright** с интеллектуальным планированием через **DeepSeek API**.  
Предназначена для работы с современными веб-приложениями, включая **SPA** с динамическими фильтрами и защитой от ботов.

---

##  Возможности

-  AI-планирование** — генерация стратегий парсинга через DeepSeek API или эвристический фолбэк  
-  Браузерная автоматизация** — Playwright с поддержкой SPA, stealth-режимом и ротацией прокси  
-  Обход защиты** — stealth-техники, решение капч, смена User-Agent и cookie-jar  
-  Капча-сервисы** — интеграция с 2Captcha для reCAPTCHA, hCaptcha и image captcha  
-  Сохранение данных** — PostgreSQL для метаданных, Redis для очередей, MinIO для HTML-снимков и файлов  
-  Экспорт** — поддержка CSV, Excel и JSON  
-  Продолжение работы** — возобновление прерванных сессий после сбоев  

---

##  Быстрый старт

### Требования

- Python **3.11+**
- [Poetry](https://python-poetry.org/) — управление зависимостями
- **Docker** и **docker-compose** — для инфраструктурных сервисов (Postgres, Redis, MinIO)

---

###  Установка

1. **Установите зависимости:**
   ```bash
   poetry install
   poetry run playwright install
   ```

2. **Настройте окружение:**
   ```bash
   cp .env.example .env
   # Отредактируйте .env и добавьте ваши API-ключи
   ```

3. **Запустите инфраструктуру:**
   ```bash
   docker compose up -d postgres redis minio
   ```

---

##  Использование

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

---

## Архитектура

- Core:** Python 3.11, Playwright, AsyncIO  
- AI Layer:** DeepSeek API (LLM-планирование действий)  
- Storage:** PostgreSQL, Redis, MinIO (S3-совместимый стор)  
- Exports:** CSV, Excel, JSON  
- CLI: чистая архитектура, типизация, структура модулей по слоям  






