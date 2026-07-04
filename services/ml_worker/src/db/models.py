from __future__ import annotations

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user", nullable=False)
    is_active = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True)
    user_id = Column(
        String, ForeignKey("users.id"), nullable=False, index=True
    )
    title = Column(String, default="")
    constraints = Column(Text, default="")
    weights = Column(JSON, default=dict)
    status = Column(String, default="created")
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True)
    session_id = Column(
        String, ForeignKey("sessions.id"), nullable=False, index=True
    )
    role = Column(String, default="user", nullable=False)
    content = Column(Text, default="")
    iteration = Column(Integer, default=0)
    status = Column(String, default="queued")
    task_id = Column(String, default="")
    created_at = Column(DateTime, default=func.now(), nullable=False)


class UploadedFile(Base):
    __tablename__ = "files"

    id = Column(String, primary_key=True)
    session_id = Column(
        String, ForeignKey("sessions.id"), nullable=False, index=True
    )
    message_id = Column(
        String, ForeignKey("messages.id"), nullable=False, index=True
    )
    original_name = Column(String, default="")
    storage_path = Column(String, nullable=False)
    mime_type = Column(String, default="")
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
    message_id = Column(
        String, ForeignKey("messages.id"), nullable=False, index=True
    )
    hypothesis_json = Column(Text, default="")
    review_json = Column(Text, default="")
    graph_json = Column(Text, default="")
    created_at = Column(DateTime, default=func.now(), nullable=False)
