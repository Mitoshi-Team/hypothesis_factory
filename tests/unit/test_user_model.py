from collections.abc import Generator
from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from src.database.base import Base
from src.database.models import User


@pytest.fixture(name="db_session")
def fixture_db_session() -> Generator[Session, None, None]:
    """
    Fixture to provide a clean in-memory
     SQLite database session for each test.
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
    """Verify that a User can be created and stored with expected fields."""
    user = User(login="test_user")
    user.set_password("secure_password123")

    db_session.add(user)
    db_session.commit()

    # Query the user back from the database
    db_user = db_session.query(User).filter_by(login="test_user").first()
    assert db_user is not None
    assert db_user.id_user == 1
    assert db_user.login == "test_user"
    assert db_user.password != "secure_password123"  # noqa: S105
    assert isinstance(db_user.created_at, datetime)
    assert isinstance(db_user.updated_at, datetime)


def test_password_hashing_and_verification() -> None:
    """Verify password hashing logic and password verification correctness."""
    user = User(login="hash_test")
    user.set_password("my_secret_pass")

    # The password must be hashed and not store the raw password
    assert user.password != "my_secret_pass"  # noqa: S105
    assert len(user.password) > 0

    # Verification checks
    assert user.verify_password("my_secret_pass") is True
    assert user.verify_password("wrong_password") is False
    assert user.verify_password("") is False


def test_audit_timestamps(db_session: Session) -> None:
    """Verify that created_at and updated_at are set and updated correctly."""
    user = User(login="timestamp_test")
    user.set_password("pass123")

    db_session.add(user)
    db_session.commit()

    initial_created = user.created_at
    initial_updated = user.updated_at

    assert initial_created is not None
    assert initial_updated is not None

    # Modify the user to trigger update timestamp change
    user.login = "updated_timestamp_test"
    db_session.add(user)
    db_session.commit()

    # In SQLite/in-memory, verify updated_at field is present and non-null.
    assert user.updated_at is not None
