"""Declarative SQLAlchemy models for the API Gateway service."""

from typing import Any, Optional

import bcrypt
from sqlalchemy import Boolean, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.base import Base


class User(Base):
    """User database model representation.

    Stores the user credentials and role, with the password stored securely
    as a bcrypt hash.

    Attributes:
        id: Unique primary key string (format usr_xxx).
        username: Unique username handle.
        hashed_password: Hashed bcrypt representation of the password.
        role: User role, either 'admin' or 'user'.
        is_active: Flag indicating if user is active.
    """

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    username: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    sessions: Mapped[list["Session"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def set_password(self, password: str) -> None:
        """Hash a plain text password and update the hashed_password column.

        Args:
            password: Clear text password to be hashed and stored.
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        self.hashed_password = hashed.decode("utf-8")

    def verify_password(self, password: str) -> bool:
        """Verify a plain text password against the stored bcrypt hash.

        Args:
            password: Clear text password to verify.

        Returns:
            bool: True if password matches the hash, False otherwise.
        """
        return bcrypt.checkpw(
            password.encode("utf-8"), self.hashed_password.encode("utf-8")
        )


class Session(Base):
    """Session database model representation.

    Tracks a user's work session, including title, constraints, weights, and status.

    Attributes:
        id: Unique primary key string (format sess_xxx).
        user_id: Foreign key string referencing the session owner.
        title: Friendly title for the session.
        constraints: Optional text describing environmental limits or requirements.
        weights: Optional dictionary of evaluation criteria weights.
        status: String indicating current status (created, processing, done, failed).
    """

    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    constraints: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    weights: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="created", nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="sessions")
    messages: Mapped[list["Message"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    files: Mapped[list["File"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    ner_entities: Mapped[list["NEREntity"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    pipeline_results: Mapped[list["PipelineResult"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )


class Message(Base):
    """Message database model representation.

    Stores conversation elements, tracking role, content, status, and execution ids.

    Attributes:
        id: Unique primary key string (format msg_xxx).
        session_id: Foreign key string referencing the session.
        role: Sender role ('user' or 'system').
        content: Text content of the message.
        iteration: Iteration index in the session.
        status: Delivery/processing status (queued, processing, done, failed).
        task_id: Associated Celery task identifier.
    """

    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    session_id: Mapped[str] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # "user" or "system"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    iteration: Mapped[int] = mapped_column(default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="queued", nullable=False)
    task_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relationships
    session: Mapped["Session"] = relationship(back_populates="messages")
    files: Mapped[list["File"]] = relationship(back_populates="message")
    pipeline_results: Mapped[list["PipelineResult"]] = relationship(
        back_populates="message", cascade="all, delete-orphan"
    )


class File(Base):
    """File database model representation.

    Stores details for uploaded attachments.

    Attributes:
        id: Unique primary key string (format file_xxx).
        session_id: Foreign key string referencing the session.
        message_id: Optional foreign key referencing the triggering message.
        original_name: Original file name.
        storage_path: Physical location on the server file system.
        mime_type: File content MIME type.
    """

    __tablename__ = "files"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    session_id: Mapped[str] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False
    )
    message_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("messages.id", ondelete="SET NULL"), nullable=True
    )
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    session: Mapped["Session"] = relationship(back_populates="files")
    message: Mapped[Optional["Message"]] = relationship(back_populates="files")


class NEREntity(Base):
    """NER Entity database model representation.

    Stores named entities extracted from context files.

    Attributes:
        id: Auto-incrementing integer key.
        session_id: Foreign key referencing the session.
        entity_id: String ID from the processing pipeline.
        name: Name text of the entity.
        label: Entity category label.
        source_file: Source document path.
    """

    __tablename__ = "ner_entities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False
    )
    entity_id: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    source_file: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    session: Mapped["Session"] = relationship(back_populates="ner_entities")


class PipelineResult(Base):
    """Pipeline Result database model representation.

    Stores JSON results output by ml_worker tasks.

    Attributes:
        id: Auto-incrementing integer key.
        session_id: Foreign key referencing the session.
        message_id: Foreign key referencing the message.
        hypothesis_json: Hashed JSON payload describing the generated hypothesis.
        review_json: Hashed JSON payload describing the expert review.
        graph_json: Hashed JSON payload describing the knowledge graph nodes and edges.
    """

    __tablename__ = "pipeline_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False
    )
    message_id: Mapped[str] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE"), nullable=False
    )
    hypothesis_json: Mapped[str] = mapped_column(Text, nullable=False)
    review_json: Mapped[str] = mapped_column(Text, nullable=False)
    graph_json: Mapped[str] = mapped_column(Text, nullable=False)
    trace_json: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # Relationships
    session: Mapped["Session"] = relationship(back_populates="pipeline_results")
    message: Mapped["Message"] = relationship(back_populates="pipeline_results")
