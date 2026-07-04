# ML Worker

Фоновый ML/Celery worker для Hypothesis Factory.

## Что делает

Worker принимает Celery-задачу `process_message` от API Gateway и выполняет полный pipeline для одного сообщения в сессии:

1. **Ingestion** - парсит PDF, Word, Excel, Markdown, TXT и SQLite/DB файлы в единую модель `UnifiedDocument`.
2. **NER** - извлекает сущности (материалы, процессы, свойства, параметры) с помощью GLiNER.
3. **Chunking + Embeddings** - разбивает документ на чанки и строит эмбеддинги через Yandex AI Studio (OpenAI-совместимый API).
4. **RAG** - извлекает релевантные фрагменты из ChromaDB и истории сессий.
5. **Knowledge Graph** - строит граф сущностей и связей.
6. **Generation** - генерирует гипотезу с оценками по новизне, реализуемости, эффекту и рискам. На итерациях после первой учитывает `previous_hypothesis` и `previous_review`.
7. **Review** - ревьюер переоценивает гипотезу и даёт вердикт.
8. **Report** - сохраняет результат в `PipelineResult`, JSON- и HTML-отчёты в `REPORT_DIR/{session_id}/{message_id}/`.

## Зависимости

Основные тяжёлые зависимости: PyTorch, GLiNER, ChromaDB, NumPy, pandas. Все они перечислены в `pyproject.toml`.

## Запуск

### Вместе со всеми сервисами (рекомендуется)

```bash
cp .env.example .env
# заполните YANDEX_API_KEY, YANDEX_FOLDER_ID и при необходимости REPORT_DIR
docker compose up -d
```

### Локально для разработки

1. Поднимите инфраструктуру:

```bash
docker compose up -d postgres redis chroma
```

2. Скопируйте и заполните `.env` в директории `services/ml_worker`:

```bash
cd services/ml_worker
cp .env.example .env
# заполните YANDEX_API_KEY, YANDEX_FOLDER_ID и при необходимости REPORT_DIR
```

3. Установите зависимости:

```bash
uv sync
```

4. Запустите Celery worker:

```bash
uv run celery -A src.celery_app worker -l info -c 1
```

Worker будет слушать задачи из Redis.

## Конфигурация

Настройки задаются через переменные окружения. Скопируйте `.env.example` из корня репозитория в `services/ml_worker/.env` и заполните:

- `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` - Redis.
- `POSTGRES_DSN` - DSN для доступа к БД (например `postgresql://...`).
- `CHROMA_HOST`, `CHROMA_PORT` - ChromaDB.
- `YANDEX_API_KEY`, `YANDEX_FOLDER_ID` - доступ к Yandex AI Studio через OpenAI-совместимый API.
- `YANDEX_EMBED_MODEL`, `YANDEX_LLM_MODEL`, `YANDEX_LLM_TEMPERATURE`, `YANDEX_LLM_MAX_TOKENS` - модели и параметры генерации.
- `NER_MODEL_NAME` - модель GLiNER для NER (по умолчанию `urchade/gliner_multi-v2.1`).
- `HF_TOKEN` - токен HuggingFace для скачивания приватных/квотируемых моделей.
- `REPORT_DIR` - директория для сохранения отчётов.
- `ML_WORKER_ENV_FILE` - путь к env-файлу (по умолчанию `.env`).

Для локальной разработки установите `REPORT_DIR=./reports`, чтобы worker мог сохранять отчёты без прав на `/app`.

## Контракт с API Gateway

Worker ожидает задачу `src.tasks.process_message.process_message` с обязательным аргументом `message_id: str`.

## Структура

- `src/ai_pipeline/` - основной pipeline: state, agents, RAG, vector store, graph.
- `src/ner/` - ingestion документов и NER.
- `src/tasks/` - Celery задачи (`process_message`).
- `src/db/` - SQLAlchemy модели и подключение к БД.
- `src/report/` - сохранение JSON/HTML отчётов.
- `src/storage/` - разрешение путей к загруженным файлам.
- `tests/` - unit-тесты.

## Тесты

Unit-тесты изолированы от тяжёлых зависимостей (numpy, chromadb, torch). Запуск:

```bash
cd services/ml_worker
uv run pytest -v
```
