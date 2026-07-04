# Фабрика гипотез

Интеллектуальный инструмент для генерации и приоритизации научно-технологических гипотез в НИИ и промышленных лабораториях.

## Архитектура

Проект представляет собой монорепозиторий на `uv` с несколькими сервисами:

- `services/api_gateway` - HTTP API для пользователей (FastAPI): аутентификация, сессии, загрузка файлов, запуск задач.
- `services/ml_worker` - фоновый ML/Celery worker: ingestion документов, NER, RAG, генерация и ревью гипотез.
- `services/frontend` - веб-интерфейс (MVP).

Инфраструктура поднимается через `docker-compose.yaml`:

- PostgreSQL - пользователи, сессии, сообщения, результаты.
- Redis - брокер Celery.
- ChromaDB - векторное хранилище.

## Быстрый старт

1. Скопируйте `.env.example` в `.env` и заполните переменные:

```bash
cp .env.example .env
```

2. Запустите инфраструктуру и сервисы:

```bash
docker compose up -d
```

3. API Gateway будет доступен по адресу `http://localhost:8000`, ChromaDB - `http://localhost:8001`.

## Локальная разработка

Проект использует `uv` для управления зависимостями. Чтобы установить все
необходимые dev-зависимости (линтеры, форматеры, pre-commit), выполните:

```bash
uv sync --group dev
```

После этого инструменты `ruff`, `mdformat` и `pre-commit` станут доступны в
окружении проекта.

### Pre-commit

Хуки настраиваются через `.pre-commit-config.yaml` и используют локальные
утилиты из dev-зависимостей. Для установки хуков выполните:

```bash
pre-commit install
# Или через uv
uv run pre-commit install
```

Чтобы проверить все файлы вручную до коммита:

```bash
pre-commit run --all-files
# Или через uv
uv run pre-commit run --all-files
```

Хуки будут запускаться автоматически при каждом `git commit`.

## Переменные окружения

Основные переменные описаны в `.env.example`:

- `POSTGRES_*` - подключение к PostgreSQL.
- `DATABASE_URL` - DSN для SQLAlchemy/AsyncPG.
- `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` - подключение к Redis.
- `CHROMA_HOST`, `CHROMA_PORT` - подключение к ChromaDB.
- `SECRET_KEY` - ключ для подписи JWT.
- `YANDEX_API_KEY`, `YANDEX_FOLDER_ID` - доступ к Yandex AI Studio.

## Ветки разработки

- `main` - инфраструктура, ML worker, корневые файлы.
- `services/api_gateway` - разработка API Gateway.
- `services/frontend` - разработка фронтенда.
