from __future__ import annotations

import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import settings

logger = logging.getLogger(__name__)

_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        dsn = os.environ.get("POSTGRES_DSN", settings.postgres_dsn)
        _engine = create_engine(dsn)
    return _engine


class SessionLocal:
    def __call__(self, *args, **kwargs):
        return sessionmaker(bind=_get_engine())(*args, **kwargs)

    def __enter__(self):
        self._session = sessionmaker(bind=_get_engine())()
        return self._session.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._session.__exit__(exc_type, exc_val, exc_tb)


__all__ = ["SessionLocal"]
