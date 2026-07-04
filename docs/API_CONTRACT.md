# API Contract: Hypothesis Factory

Версия: 0.1.0
Базовый URL: `http://localhost:8000/api/v1`

## Общее

- Все запросы, кроме `/auth/login` и `/auth/refresh`, требуют заголовок `Authorization: Bearer <token>`.
- Access token действует 15 минут, refresh token — 7 дней.
- Дата/время передаются в формате ISO 8601 UTC.
- Идентификаторы генерируются на стороне API Gateway в формате `prefix_uuid4-short`:
  - пользователь: `usr_xxx`,
  - сессия: `sess_xxx`,
  - сообщение: `msg_xxx`,
  - файл: `file_xxx`,
  - результат: `res_xxx`.
- Файлы хранятся в локальной директории `UPLOAD_DIR` (по умолчанию `/app/uploads`).
- Отчёты хранятся в локальной директории `REPORT_DIR` (по умолчанию `/app/reports`).
- Пути к файлам передаются в `ml_worker` как абсолютные пути в файловой системе контейнера, например `/app/uploads/sess_xxx/file_xxx.pdf`.
- В продакшене `UPLOAD_DIR` и `REPORT_DIR` должны быть заменены на S3/MinIO или NAS.
- Ошибки возвращаются в едином формате:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed.",
    "details": {
      "body.problem_statement": ["field required"]
    }
  }
}
```

## Общая схема базы данных

API Gateway и ml_worker используют общую PostgreSQL. Ниже минимальный набор таблиц.

### `users`

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | string PK | `usr_xxx` |
| `username` | string unique | Логин |
| `hashed_password` | string | bcrypt-хеш |
| `role` | string | `admin` или `user` |
| `is_active` | bool | Активен ли пользователь |
| `created_at` | datetime | Время создания |

### `sessions`

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | string PK | `sess_xxx` |
| `user_id` | string FK | Владелец |
| `title` | string | Название |
| `constraints` | text | Ограничения |
| `weights` | jsonb | Веса критериев |
| `status` | string | `created`, `processing`, `done`, `failed` |
| `created_at` | datetime | Время создания |
| `updated_at` | datetime | Время обновления |

### `messages`

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | string PK | `msg_xxx` |
| `session_id` | string FK | Сессия |
| `role` | string | `user` или `system` |
| `content` | text | Текст |
| `iteration` | int | Номер итерации |
| `status` | string | `queued`, `processing`, `done`, `failed` |
| `task_id` | string | ID Celery-задачи |
| `created_at` | datetime | Время создания |

### `files`

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | string PK | `file_xxx` |
| `session_id` | string FK | Сессия |
| `message_id` | string FK | Сообщение |
| `original_name` | string | Исходное имя файла |
| `storage_path` | string | Путь в `UPLOAD_DIR` |
| `mime_type` | string | MIME-тип |
| `created_at` | datetime | Время загрузки |

### `ner_entities`

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | int PK autoincrement | |
| `session_id` | string FK | Сессия |
| `entity_id` | string | ID сущности из pipeline |
| `name` | string | Имя сущности |
| `label` | string | Тип сущности |
| `source_file` | string | Источник |

### `pipeline_results`

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | int PK autoincrement | |
| `session_id` | string FK | Сессия |
| `message_id` | string FK | Системное сообщение-результат |
| `hypothesis_json` | text | JSON гипотезы |
| `review_json` | text | JSON ревью |
| `graph_json` | text | JSON графа |
| `created_at` | datetime | Время создания |

## Коды ошибок

| Код | HTTP | Описание |
|-----|------|----------|
| `VALIDATION_ERROR` | 422 | Ошибка валидации входных данных |
| `UNAUTHORIZED` | 401 | Неверный или отсутствующий токен |
| `FORBIDDEN` | 403 | Недостаточно прав |
| `NOT_FOUND` | 404 | Ресурс не найден |
| `INTERNAL_SERVER_ERROR` | 500 | Внутренняя ошибка сервера |

## Auth

### Роли

| Значение | Описание |
|----------|----------|
| `admin` | Создание пользователей, полный доступ |
| `user` | Работа со своими сессиями |

### POST /auth/login

Аутентификация пользователя. Выдаёт access token и refresh token.

**Request:**

```json
{
  "username": "researcher_1",
  "password": "secure-password"
}
```

**Response 200:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example",
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4.example",
  "token_type": "bearer"
}
```

### POST /auth/refresh

Обновление access token по refresh token.

**Request:**

```json
{
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4.example"
}
```

**Response 200:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example",
  "token_type": "bearer"
}
```

## Admin

### POST /admin/users

Создание нового пользователя. Только для роли `admin`. Поле `password` передаётся в открытом виде, API Gateway хранит только bcrypt-хеш.

**Request:**

```json
{
  "username": "researcher_2",
  "password": "initial-password",
  "role": "user"
}
```

**Response 201:**

```json
{
  "id": "usr_abc123",
  "username": "researcher_2",
  "role": "user",
  "is_active": true,
  "created_at": "2026-07-04T10:00:00Z"
}
```

## Sessions

### POST /sessions

Создать новую сессию. Ограничения и веса критериев задаются один раз при создании и сохраняются в таблице `sessions`. При последующих сообщениях API Gateway передаёт их в `ml_worker` автоматически.

**Request:**

```json
{
  "title": "Повышение жаропрочности сплава",
  "constraints": "Бюджет 5 млн руб. Оборудование: печь X. Норматив: ГОСТ 12345.",
  "weights": {
    "novelty": 1.5,
    "feasibility": 1.0,
    "effect": 2.0,
    "risk": 0.5
  }
}
```

**Response 201:**

```json
{
  "id": "sess_abc123",
  "title": "Повышение жаропрочности сплава",
  "constraints": "Бюджет 5 млн руб. Оборудование: печь X. Норматив: ГОСТ 12345.",
  "weights": {
    "novelty": 1.5,
    "feasibility": 1.0,
    "effect": 2.0,
    "risk": 0.5
  },
  "status": "created",
  "created_at": "2026-07-04T10:00:00Z",
  "updated_at": "2026-07-04T10:00:00Z"
}
```

### GET /sessions

Список сессий текущего пользователя.

**Response 200:**

```json
{
  "items": [
    {
      "id": "sess_abc123",
      "title": "Повышение жаропрочности сплава",
      "status": "done",
      "created_at": "2026-07-04T10:00:00Z",
      "updated_at": "2026-07-04T10:30:00Z"
    }
  ],
  "total": 1
}
```

### GET /sessions/{session_id}

Полная история сессии: метаданные, сообщения, последний результат.

**Response 200:**

```json
{
  "id": "sess_abc123",
  "title": "Повышение жаропрочности сплава",
  "constraints": "Бюджет 5 млн руб. Оборудование: печь X. Норматив: ГОСТ 12345.",
  "weights": {
    "novelty": 1.5,
    "feasibility": 1.0,
    "effect": 2.0,
    "risk": 0.5
  },
  "status": "done",
  "created_at": "2026-07-04T10:00:00Z",
  "updated_at": "2026-07-04T10:30:00Z",
  "messages": [
    {
      "id": "msg_def456",
      "role": "user",
      "content": "Как повысить жаропрочность сплава Х на 15%?",
      "iteration": 0,
      "status": "done",
      "task_id": "task_ghi789",
      "created_at": "2026-07-04T10:05:00Z"
    },
    {
      "id": "msg_jkl012",
      "role": "system",
      "content": "Сгенерирована гипотеза...",
      "iteration": 0,
      "status": "done",
      "task_id": "task_ghi789",
      "created_at": "2026-07-04T10:06:00Z"
    }
  ],
  "latest_result": {
    "message_id": "msg_jkl012",
    "hypothesis": { ... },
    "review": { ... },
    "graph": { ... }
  }
}
```

### DELETE /sessions/{session_id}

Удалить сессию и все связанные данные.

**Response 204:** пустое тело.

## Messages

### POST /sessions/{session_id}/messages

Отправить сообщение в сессию с возможностью загрузки файлов. Запускает Celery-задачу.

**Content-Type:** `multipart/form-data`

**Поля:**

| Поле | Тип | Обязательный | Описание |
|------|-----|--------------|----------|
| `content` | string | да | Проблема/запрос пользователя |
| `files` | file[] | нет | Загружаемые файлы (PDF, DOCX, XLSX, TXT, MD, DB) |

**Response 202:**

```json
{
  "message_id": "msg_jkl012",
  "task_id": "task_ghi789",
  "status": "queued"
}
```

Поле `iteration` для сообщения вычисляется API Gateway как количество предыдущих пар сообщение-ответ в сессии. `first_message` для Celery равно `True`, если `iteration == 0`.

### GET /sessions/{session_id}/messages

Список сообщений сессии с пагинацией.

**Query parameters:**

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `page` | integer | 1 | Номер страницы |
| `page_size` | integer | 20 | Размер страницы (максимум 100) |

**Response 200:**

```json
{
  "items": [
    {
      "id": "msg_def456",
      "role": "user",
      "content": "Как повысить жаропрочность сплава Х на 15%?",
      "iteration": 0,
      "status": "done",
      "task_id": "task_ghi789",
      "created_at": "2026-07-04T10:05:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

## Results

### GET /sessions/{session_id}/results/{message_id}

Получить результат обработки сообщения.

**Response 200 (если готово):**

```json
{
  "message_id": "msg_jkl012",
  "status": "done",
  "hypothesis": {
    "title": "Добавка ниобия в сплав Х",
    "problem": "Повысить жаропрочность сплава Х на 15%",
    "hypothesis": "Добавка 0.3% ниобия в сплав Х при режиме отжига Y повысит жаропрочность за счёт формирования дисперсных карбидов.",
    "expected_effect": "Повышение жаропрочности на 15-18% при 1100°C",
    "risks": ["Перерасход ниобия", "Изменение пластичности"],
    "feasibility_score": 7.5,
    "novelty_score": 6.0,
    "effect_score": 8.0,
    "risk_score": 4.0,
    "evidence_sources": ["doc_001", "doc_002"],
    "supporting_nodes": ["ent_abc", "ent_def"],
    "source_chunks": ["chunk_001", "chunk_002"]
  },
  "review": {
    "hypothesis_id": "Добавка ниобия в сплав Х",
    "scores": {
      "novelty": 6,
      "feasibility": 8,
      "effect": 8,
      "risk": 4
    },
    "comments": {
      "novelty": "Идея известна, но дозировка конкретна.",
      "general": "Гипотеза проверяема и релевантна."
    },
    "verdict": "accept",
    "suggestions": ["Уточнить диапазон температур отжига."]
  },
  "graph": {
    "nodes": [...],
    "edges": [...],
    "chains": [...]
  },
  "trace": {
    "session_id": "sess_abc123",
    "iteration": 0,
    "chunks_used": ["chunk_001"],
    "tables_queried": [],
    "history_cases_used": []
  }
}
```

**Response 202 (если в обработке):**

```json
{
  "message_id": "msg_jkl012",
  "status": "processing",
  "task_id": "task_ghi789"
}
```

## Graph

### GET /sessions/{session_id}/graph

Получить knowledge graph для последнего результата сессии.

**Response 200:**

```json
{
  "nodes": [
    {
      "id": "ent_abc",
      "label": "Material",
      "name": "ниобий",
      "source_chunks": [
        {
          "chunk_id": "chunk_001",
          "element_id": "el_001",
          "text": "...",
          "document_title": "...",
          "section_path": "..."
        }
      ],
      "metadata": {}
    }
  ],
  "edges": [
    {"source": "ent_abc", "target": "ent_def", "relation": "influences", "confidence": 0.9, "metadata": {}}
  ],
  "chains": [
    {"chain_id": "ch_001", "node_ids": ["ent_abc", "ent_def"], "edge_labels": ["influences"], "summary": "influences"}
  ]
}
```

#### SourceRef

| Поле | Тип | Описание |
|------|-----|----------|
| `chunk_id` | string | ID исходного чанка |
| `element_id` | string | ID элемента документа |
| `text` | string | Текст чанка |
| `document_title` | string | Название документа |
| `section_path` | string | Путь раздела в документе |

### Типы узлов (node.label)

| Значение | Описание |
|----------|----------|
| `Material` | Материал, сплав, элемент, соединение |
| `Process` | Технологический процесс (отжиг, прокатка и т.д.) |
| `Property` | Свойство материала (жаропрочность, прочность и т.д.) |
| `Parameter` | Параметр процесса (температура, дозировка, время) |

### Типы рёбер (edge.relation)

| Значение | Описание |
|----------|----------|
| `contains` | Содержит в себе |
| `influences` | Влияет на |
| `produces` | Производит / образует |
| `requires` | Требует / нуждается в |
| `cites` | Цитирует / ссылается |
| `part_of` | Является частью |
| `similar_to` | Похож на |

## Reports

### GET /sessions/{session_id}/reports/latest

Скачать последний отчёт. Формат определяется заголовком `Accept`:

- `Accept: application/json` — JSON-отчёт.
- `Accept: text/html` — HTML-отчёт.

По умолчанию возвращается JSON.

**Response 200:** файл отчёта.

## Tasks

### GET /tasks/{task_id}

Получить статус Celery-задачи.

**Response 200:**

```json
{
  "task_id": "task_ghi789",
  "status": "PENDING",
  "result": null
}
```

Возможные статусы: `PENDING`, `STARTED`, `SUCCESS`, `FAILURE`, `RETRY`.

## Статусы сущностей

### Session.status

- `created` — сессия создана.
- `processing` — выполняется обработка сообщения.
- `done` — последнее сообщение обработано.
- `failed` — последнее сообщение завершилось с ошибкой.

### Message.status

- `queued` — поставлено в очередь Celery.
- `processing` — worker взял задачу.
- `done` — обработка завершена.
- `failed` — обработка завершилась с ошибкой.

## Seed-скрипт администратора

Для создания первого администратора используется скрипт:

```bash
cd services/api_gateway
uv run python -m scripts.create_admin --username admin --password admin-password
```

Скрипт создаёт пользователя с ролью `admin`, если он ещё не существует. Рекомендуется выполнить его один раз после первого развёртывания.

## Связь с ml_worker

API Gateway при получении `POST /sessions/{session_id}/messages` вызывает Celery-задачу `process_message` из `services/ml_worker/src/tasks/process_message.py` со следующими аргументами:

```python
process_message.delay(
    user_id=user_id,
    uuid=session_id,
    message_id=message_id,
    first_message=is_first_message,
    upload_files=["/app/uploads/sess_abc123/file_xxx.pdf", ...],
    prompt=content,
)
```

Параметры:

| Параметр | Тип | Описание |
|----------|-----|----------|
| `user_id` | string | ID пользователя из JWT |
| `uuid` | string | ID сессии |
| `message_id` | string | ID системного сообщения, под которым будет сохранён результат |
| `first_message` | bool | `True`, если это первое сообщение в сессии |
| `upload_files` | list[str] | Абсолютные пути к загруженным файлам |
| `prompt` | string | Текст сообщения пользователя |

Ограничения и веса берутся из сессии и передаются в pipeline внутри worker.

Worker выполняет pipeline и сохраняет результат. API Gateway затем читает результат из таблицы `pipeline_results` по `session_id` и `message_id` и отдаёт клиенту.

### Ожидаемое поведение ml_worker

1. Получить задачу с аргументами `user_id`, `uuid`, `message_id`, `first_message`, `upload_files`, `prompt`.
2. Прочитать сессию из PostgreSQL по `uuid`, извлечь `constraints` и `weights`.
3. Определить `iteration` как количество уже обработанных сообщений в сессии (или `0`, если `first_message=True`).
4. Если `iteration > 0`, взять предыдущую гипотезу и сообщение пользователя как `feedback`.
5. Выполнить pipeline: ingestion, NER, chunking, RAG, graph, generation, review.
6. Сохранить результат в таблицу `pipeline_results`:
   - `session_id` = `uuid`,
   - `message_id` = id системного сообщения, созданного API Gateway,
   - `hypothesis_json`, `review_json`, `graph_json`.
7. Обновить статус системного сообщения на `done` или `failed`.
8. Сохранить отчёт в `REPORT_DIR/{session_id}/{message_id}.json` (и `.html`, если реализовано).
