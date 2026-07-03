# Фабрика гипотез

## Локальная разработка

### Установка зависимостей

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

## Запуск сервисов

### API Gateway

API Gateway предоставляет REST API для взаимодействия с системой «Фабрика гипотез».

Для запуска API Gateway локально в режиме разработки выполните команду из корня проекта:

```bash
uv run --package api-gateway uvicorn src.main:app --reload
```

Или из директории самого сервиса:

```bash
cd services/api_gateway
uv run uvicorn src.main:app --reload
```

После запуска сервис будет доступен по следующим адресам:

- **Интерактивная документация (Swagger UI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Альтернативная документация (ReDoc):** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Проверка статуса (Health Check):** [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)
