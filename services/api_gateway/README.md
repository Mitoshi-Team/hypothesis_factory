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
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

## Конфигурация

Настройки задаются через переменные окружения (см. `.env.example` в корне):

- `DATABASE_URL` — PostgreSQL через asyncpg.
- `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` — Redis.
- `SECRET_KEY` — ключ для подписи JWT.
- `UPLOAD_DIR` — директория для загружаемых файлов.
- `ENVIRONMENT`, `DEBUG`, `HOST`, `PORT`, `CORS_ORIGINS`, `API_PREFIX`.

## Структура

- `src/main.py` — точка входа FastAPI.
- `src/config.py` — настройки.
- `src/api/router.py` — маршруты API.
- `src/api/schemas.py` — Pydantic-схемы.
- `src/api/dependencies.py` — зависимости FastAPI.
- `src/utils/exceptions.py` — кастомные исключения.
- `src/utils/log_config.py` — логирование.
- `Dockerfile` — образ сервиса.
- `tests/` — unit и integration тесты.

## Тесты

```bash
cd services/api_gateway
uv run pytest
```
