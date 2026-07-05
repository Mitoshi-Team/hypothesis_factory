# Фабрика гипотез

Интеллектуальный инструмент для генерации и приоритизации научно-технологических гипотез в НИИ и промышленных лабораториях.

## Архитектура

Проект представляет собой монорепозиторий на `uv` с несколькими сервисами:

- `services/api_gateway` — HTTP API для пользователей (FastAPI): аутентификация, сессии, загрузка файлов, запуск задач.
- `services/ml_worker` — фоновый ML/Celery worker: ingestion документов, NER, RAG, генерация и ревью гипотез.
- `services/frontend` — веб-интерфейс (React + Vite).

Инфраструктура поднимается через `docker-compose.yaml`:

- PostgreSQL — пользователи, сессии, сообщения, результаты.
- Redis — брокер Celery.
- ChromaDB — векторное хранилище.

## Быстрый старт

1. Скопируйте `.env.example` в `.env` и заполните обязательные переменные:

```bash
cp .env.example .env
```

Обязательно задайте:

- `YANDEX_API_KEY` — ключ доступа к Yandex AI Studio.
- `YANDEX_FOLDER_ID` — идентификатор каталога Yandex Cloud.

Остальные переменные заполнены разумными значениями по умолчанию.

2. Запустите инфраструктуру и сервисы:

```bash
docker compose up -d
```

3. Создайте первого администратора:

```bash
uv run --package api-gateway python scripts/create_admin.py admin <password>
```

Или внутри запущенного контейнера:

```bash
docker compose exec api_gateway /app/.venv/bin/python /app/scripts/create_admin.py admin <password>
```

4. Откройте веб-интерфейс:

- Frontend: `http://localhost:4173`
- API Gateway: `http://localhost:8000`
- Документация API: `http://localhost:8000/docs`

По умолчанию frontend в Docker обращается к API по относительному пути `/api/v1`, что позволяет использовать один домен с nginx. Для локальной разработки вне Docker можно переопределить адрес:

```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1 npm run dev
```

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

- `POSTGRES_*` — подключение к PostgreSQL.
- `POSTGRES_DSN` / `DATABASE_URL` — DSN для ML Worker и API Gateway.
- `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` — подключение к Redis.
- `CHROMA_HOST`, `CHROMA_PORT` — подключение к ChromaDB.
- `SECRET_KEY` — ключ для подписи JWT.
- `YANDEX_API_KEY`, `YANDEX_FOLDER_ID` — доступ к Yandex AI Studio.
- `YANDEX_EMBED_MODEL`, `YANDEX_LLM_MODEL` — модели для эмбеддингов и генерации.
- `YANDEX_LLM_TEMPERATURE`, `YANDEX_LLM_MAX_TOKENS` — параметры генерации.
- `NER_MODEL_NAME`, `HF_TOKEN` — модель GLiNER и токен HuggingFace.
- `API_GATEWAY_PORT`, `FRONTEND_PORT` — внешние порты сервисов.
- `UPLOAD_DIR` — директория для загружаемых файлов.
- `REPORT_DIR` — директория для отчётов ML worker.

## Статус реализации

Реализовано:

- Приём и предобработка документов (PDF, Excel, Word, Markdown, TXT, базы данных).
- Извлечение сущностей и связей (NER), построение графа знаний.
- Генерация и ревью гипотез с обоснованием, оценкой новизны, рисков и ценности.
- Валидация сгенерированных гипотез с возможностью fallback на экспертную проверку.
- Ранжирование по настраиваемым весам критериев.
- Сессионная модель: чат-проект с сохранением ограничений, весов, истории сообщений и результатов.
- Итеративное улучшение гипотез на основе предыдущих результатов (`previous_hypothesis`, `previous_review`) и RAG-истории.
- Формирование JSON/HTML отчётов по каждому сообщению.
- Docker Compose развёртывание всех сервисов.

Ещё не реализовано:

- Визуальный конструктор дорожных карт проверки гипотез с оценкой ресурсов и сроков.
- Явный механизм обучения на фидбэке эксперта (подтверждено/опровергнуто). Обратная связь учитывается косвенно через `previous_review` и RAG-историю, но в схеме БД нет отдельного статуса верификации гипотезы.

## Документация по сервисам

- [API Gateway](services/api_gateway/README.md)
- [ML Worker](services/ml_worker/README.md)
- [Frontend](services/frontend/README.md)
