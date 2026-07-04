from collections.abc import Generator
from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from src.database.base import Base
from src.database.models import (
    File,
    Message,
    NEREntity,
    PipelineResult,
    Session as UserSession,
    User,
)


@pytest.fixture(name="db_session")
def fixture_db_session() -> Generator[Session, None, None]:
    """Fixture to provide a clean in-memory SQLite database session
    for each test.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


def test_user_creation_and_attributes(db_session: Session) -> None:
    """Verify that a User can be created and stored with expected
    contract fields.
    """
    user = User(
        id="usr_test123",
        username="researcher_test",
        role="user",
        is_active=True,
    )
    user.set_password("secure_password123")

    db_session.add(user)
    db_session.commit()

    # Query the user back from the database
    db_user = db_session.query(User).filter_by(username="researcher_test").first()
    assert db_user is not None
    assert db_user.id == "usr_test123"
    assert db_user.username == "researcher_test"
    assert db_user.role == "user"
    assert db_user.is_active is True
    assert db_user.hashed_password != "secure_password123"  # noqa: S105
    assert isinstance(db_user.created_at, datetime)
    assert isinstance(db_user.updated_at, datetime)


def test_password_hashing_and_verification() -> None:
    """Verify password hashing logic and password verification correctness."""
    user = User(id="usr_hash", username="hash_test")
    user.set_password("my_secret_pass")

    # The password must be hashed and not store the raw password
    assert user.hashed_password != "my_secret_pass"  # noqa: S105
    assert len(user.hashed_password) > 0

    # Verification checks
    assert user.verify_password("my_secret_pass") is True
    assert user.verify_password("wrong_password") is False
    assert user.verify_password("") is False


def test_audit_timestamps(db_session: Session) -> None:
    """Verify that created_at and updated_at are set and updated correctly."""
    user = User(id="usr_time", username="timestamp_test")
    user.set_password("pass123")

    db_session.add(user)
    db_session.commit()

    initial_created = user.created_at
    initial_updated = user.updated_at

    assert initial_created is not None
    assert initial_updated is not None

    # Modify the user to trigger update timestamp change
    user.username = "updated_timestamp_test"
    db_session.add(user)
    db_session.commit()

    # Verify updated_at is populated
    assert user.updated_at is not None


def test_session_message_file_relations_and_cascade(
    db_session: Session,
) -> None:
    """Verify complete schema relationships and delete cascade behaviors."""
    # 1. Create a user
    user = User(id="usr_001", username="user_001")
    user.set_password("secret_pass")
    db_session.add(user)
    db_session.commit()

    # 2. Create a session associated with this user
    user_session = UserSession(
        id="sess_001",
        user_id=user.id,
        title="Flotation Optimization",
        constraints="Max 10k budget",
        weights={"novelty": 1.0, "feasibility": 1.0},
    )
    db_session.add(user_session)
    db_session.commit()

    # 3. Create a message in this session
    message = Message(
        id="msg_001",
        session_id=user_session.id,
        role="user",
        content="Optimize copper recovery rate",
        iteration=0,
        status="done",
        task_id="celery_task_123",
    )
    db_session.add(message)
    db_session.commit()

    # 4. Create a file associated with the session and message
    file_attachment = File(
        id="file_001",
        session_id=user_session.id,
        message_id=message.id,
        original_name="test_report.xlsx",
        storage_path="/app/uploads/sess_001/file_001.xlsx",
        mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    db_session.add(file_attachment)
    db_session.commit()

    # 5. Create a NER Entity
    ner_entity = NEREntity(
        session_id=user_session.id,
        entity_id="ent_copper",
        name="Copper",
        label="Material",
        source_file="test_report.xlsx",
    )
    db_session.add(ner_entity)
    db_session.commit()

    # 6. Create a Pipeline Result
    result = PipelineResult(
        session_id=user_session.id,
        message_id=message.id,
        hypothesis_json='{"formulation": "Use butyl xanthate"}',
        review_json='{"verdict": "accept"}',
        graph_json='{"nodes": [], "edges": []}',
    )
    db_session.add(result)
    db_session.commit()

    # --- Assert queries and relationships ---
    # Query back everything and check relations
    db_sess = db_session.query(UserSession).filter_by(id="sess_001").first()
    assert db_sess is not None
    assert db_sess.user.username == "user_001"
    assert len(db_sess.messages) == 1
    assert db_sess.messages[0].content == "Optimize copper recovery rate"
    assert len(db_sess.files) == 1
    assert db_sess.files[0].original_name == "test_report.xlsx"
    assert len(db_sess.ner_entities) == 1
    assert db_sess.ner_entities[0].name == "Copper"
    assert len(db_sess.pipeline_results) == 1
    assert "butyl xanthate" in db_sess.pipeline_results[0].hypothesis_json

    # Test file connection to message
    db_msg = db_session.query(Message).filter_by(id="msg_001").first()
    assert db_msg is not None
    assert len(db_msg.files) == 1
    assert db_msg.files[0].id == "file_001"

    # Test cascade delete of the User
    db_session.delete(user)
    db_session.commit()

    # Verify that the session and all associated child entities are deleted
    assert db_session.query(User).filter_by(id="usr_001").first() is None
    assert db_session.query(UserSession).filter_by(id="sess_001").first() is None
    assert db_session.query(Message).filter_by(id="msg_001").first() is None
    assert db_session.query(File).filter_by(id="file_001").first() is None
    assert db_session.query(NEREntity).filter_by(entity_id="ent_copper").first() is None
    assert db_session.query(PipelineResult).first() is None
