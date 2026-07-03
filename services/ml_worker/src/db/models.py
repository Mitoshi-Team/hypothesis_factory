from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    status = Column(String, default="processing")
    created_at = Column(DateTime, default=func.now(), nullable=False)


class NEREntity(Base):
    __tablename__ = "ner_entities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(
        String, ForeignKey("sessions.id"), nullable=False, index=True
    )
    entity_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    label = Column(String, nullable=False)
    source_file = Column(String, default="")


class PipelineResult(Base):
    __tablename__ = "pipeline_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(
        String, ForeignKey("sessions.id"), nullable=False, index=True
    )
    hypothesis_json = Column(Text, default="")
    review_json = Column(Text, default="")
    graph_json = Column(Text, default="")
    created_at = Column(DateTime, default=func.now(), nullable=False)
