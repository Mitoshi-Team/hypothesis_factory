from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import settings

engine = create_engine(settings.postgres_dsn)
SessionLocal = sessionmaker(bind=engine)
