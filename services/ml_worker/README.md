# ML Worker

Фоновый ML/Celery worker для Hypothesis Factory.

## Что делает

Worker принимает задачу от API Gateway и выполняет полный pipeline:

1. **Ingestion** - парсит PDF, Word, Excel, Markdown, TXT и SQLite/DB файлы в единую модель `UnifiedDocument`.
2. **NER** - извлекает сущности (материалы, процессы, свойства, параметры) с помощью GLiNER.
3. **Chunking + Embeddings** - разбивает документ на чанки и строит эмбеддинги через Yandex AI Studio.
4. **RAG** - извлекает релевантные фрагменты из ChromaDB и истории сессий.
5. **Knowledge Graph** - строит граф сущностей и связей.
6. **Generation** - генерирует гипотезу с оценками по новизне, реализуемости, эффекту и рискам.
7. **Review** - ревьюер переоценивает гипотезу и даёт вердикт.
8. **Report** - сохраняет результат в JSON.

## Запуск

### Через Docker Compose

```bash
docker compose up -d ml_worker
```

### Локально

Убедитесь, что запущены PostgreSQL, Redis и ChromaDB, и выполните:

```bash
cd services/ml_worker
uv run celery -A src.celery_app worker -l info -c 1
```

## Конфигурация

Настройки задаются через переменные окружения (см. `.env.example` в корне):

- `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` - Redis.
- `POSTGRES_DSN` - PostgreSQL.
- `CHROMA_HOST`, `CHROMA_PORT` - ChromaDB.
- `YANDEX_API_KEY`, `YANDEX_FOLDER_ID` - Yandex AI Studio.
- `REPORT_DIR` - директория для сохранения отчётов.

## Структура

- `src/ai_pipeline/` - основной pipeline.
- `src/ner/` - ingestion и NER.
- `src/tasks/` - Celery задачи.
- `src/db/` - SQLAlchemy модели.
- `src/report/` - сохранение отчётов.
- `tests/` - unit-тесты.
