FROM python:3.13-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.6 /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONPATH=/app

COPY pyproject.toml uv.lock ./
COPY services/ml_worker/pyproject.toml services/ml_worker/
COPY services/api_gateway/pyproject.toml services/api_gateway/

RUN uv sync --frozen --no-dev --package ml-worker

COPY services/ml_worker/src ./src

CMD ["celery", "-A", "src.celery_app", "worker", "-l", "info", "-c", "1"]
