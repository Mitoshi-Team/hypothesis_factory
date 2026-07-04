# API Gateway

HTTP API для Hypothesis Factory.

## Ответственность

API Gateway — единая точка входа для frontend и внешних клиентов. Сервис:

- управляет пользователями и аутентификацией (JWT),
- управляет сессиями и сообщениями исследователей,
- принимает файлы (патенты, статьи, отчёты, фотографии),
- ставит задачи в очередь Celery для `ml_worker`,
- возвращает статус обработки и итоговые отчёты.

## Запуск

### Через Docker Compose

```bash
docker compose up -d api_gateway
```

### Локально

Убедитесь, что запущены PostgreSQL, Redis и ChromaDB, и выполните:

```bash
cd services/api_gateway
# Запуск через python-модуль (использует порт и хост из настроек)
uv run python -m src.main

# Или прямой запуск через uvicorn
uv run uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
```

## Конфигурация

Скопируйте `.env.example` и заполните значения:

```bash
cd services/api_gateway
cp .env.example .env
```

Основные переменные:

- `DATABASE_URL` — PostgreSQL через asyncpg.
- `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` — Redis.
- `SECRET_KEY` — ключ для подписи JWT.
- `ACCESS_TOKEN_EXPIRE_MINUTES` — время жизни JWT Access токена (по умолчанию 15 минут).
- `REFRESH_TOKEN_EXPIRE_DAYS` — время жизни JWT Refresh токена (по умолчанию 7 дней).
- `UPLOAD_DIR` — директория для загружаемых файлов пользователей (должна совпадать с `ml_worker`).
- `REPORT_DIR` — директория для хранения сгенерированных отчетов (должна совпадать с `ml_worker`).
- `ENVIRONMENT`, `DEBUG`, `HOST`, `PORT`, `CORS_ORIGINS`, `API_PREFIX`.

## Структура

- `src/main.py` — точка входа FastAPI.
- `src/config.py` — настройки.
- `src/api/router.py` — главный роутер.
- `src/api/routes/` — разделенные маршруты API (auth, admin, sessions, results, tasks).
- `src/api/schemas.py` — Pydantic-схемы запросов и ответов.
- `src/api/dependencies.py` — зависимости FastAPI (БД, аутентификация, проверка прав).
- `src/database/session.py` — асинхронные сессии базы данных.
- `src/utils/auth.py` — хелперы для генерации и проверки JWT-токенов.
- `src/utils/celery_client.py` — клиент Celery для отправки задач.
- `src/utils/exceptions.py` — кастомные исключения и ошибки приложения.
- `src/utils/log_config.py` — логирование.
- `scripts/create_admin.py` — скрипт сидинга администратора.
- `Dockerfile` — образ сервиса.
- `tests/` — unit и integration тесты.

## Инициализация базы данных

Для создания первого администратора выполните скрипт инициализации:

```bash
cd services/api_gateway
uv run python -m scripts.create_admin --username admin --password admin-password
```

## Тесты

```bash
cd services/api_gateway
uv run pytest
```
