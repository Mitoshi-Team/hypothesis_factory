"""Integration tests for the API Gateway service endpoints."""

import datetime
import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.dependencies import get_db
from src.config import get_settings
from src.database.models import Message as MessageORM
from src.database.models import PipelineResult as PipelineResultORM
from src.database.models import Session as SessionORM
from src.database.models import User
from src.main import app
from src.utils.auth import ALGORITHM

settings = get_settings()


# Helper to generate test tokens
def create_test_token(
    username: str, token_type: str = "access", expires_in_minutes: int = 15
) -> str:
    payload = {
        "sub": username,
        "type": token_type,
        "exp": datetime.datetime.now(datetime.UTC)
        + datetime.timedelta(minutes=expires_in_minutes),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


# Mock DB dependency
@pytest.fixture
def mock_db() -> AsyncMock:
    db = AsyncMock(spec=AsyncSession)
    return db


@pytest.fixture
def client(mock_db: AsyncMock) -> TestClient:
    # Override get_db to return our mock DB session
    app.dependency_overrides[get_db] = lambda: mock_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_health_check(client: TestClient) -> None:
    """Test that the health check endpoint returns 200 OK."""
    response = client.get("/api/v1/health")
    assert response.status_code == status.HTTP_200_OK

    json_data = response.json()
    assert json_data["status"] == "ok"
    assert json_data["environment"] == "test"
    assert "timestamp" in json_data
    assert "version" in json_data


# --- Auth Endpoint Tests ---


def test_login_success(client: TestClient, mock_db: AsyncMock) -> None:
    """Test successful user login."""
    test_user = User(
        id="usr_test123",
        username="researcher_test",
        role="user",
        is_active=True,
    )
    test_user.set_password("correct-password")

    # Mock DB query result
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_user
    mock_db.execute.return_value = mock_result

    payload = {"username": "researcher_test", "password": "correct-password"}
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == status.HTTP_200_OK

    json_data = response.json()
    assert "access_token" in json_data
    assert "refresh_token" in json_data
    assert json_data["token_type"] == "bearer"


def test_login_fail_invalid_credentials(client: TestClient, mock_db: AsyncMock) -> None:
    """Test login failure with invalid password."""
    test_user = User(
        id="usr_test123",
        username="researcher_test",
        role="user",
        is_active=True,
    )
    test_user.set_password("correct-password")

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_user
    mock_db.execute.return_value = mock_result

    payload = {"username": "researcher_test", "password": "wrong-password"}
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_refresh_token_success(client: TestClient, mock_db: AsyncMock) -> None:
    """Test successful access token regeneration using refresh token."""
    test_user = User(
        id="usr_test123",
        username="researcher_test",
        role="user",
        is_active=True,
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_user
    mock_db.execute.return_value = mock_result

    refresh_token = create_test_token("researcher_test", token_type="refresh")

    payload = {"refresh_token": refresh_token}
    response = client.post("/api/v1/auth/refresh", json=payload)
    assert response.status_code == status.HTTP_200_OK

    json_data = response.json()
    assert "access_token" in json_data
    assert json_data["token_type"] == "bearer"


# --- Admin Endpoint Tests ---


def test_create_user_admin_only(client: TestClient, mock_db: AsyncMock) -> None:
    """Verify that creating users requires admin privileges."""
    admin_user = User(
        id="usr_admin001", username="admin_user", role="admin", is_active=True
    )
    # Mock user retrieval for JWT validation dependency
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.side_effect = [
        admin_user,  # get_current_user lookup
        None,  # check username availability lookup
    ]
    mock_db.execute.return_value = mock_result

    token = create_test_token("admin_user")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {"username": "new_user", "password": "temp-password", "role": "user"}

    response = client.post("/api/v1/admin/users", json=payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["username"] == "new_user"


def test_create_user_forbidden_for_regular_user(
    client: TestClient, mock_db: AsyncMock
) -> None:
    """Verify regular user receives 403 Forbidden for admin operations."""
    regular_user = User(
        id="usr_test123", username="regular_user", role="user", is_active=True
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = regular_user
    mock_db.execute.return_value = mock_result

    token = create_test_token("regular_user")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {"username": "new_user", "password": "temp-password", "role": "user"}
    response = client.post("/api/v1/admin/users", json=payload, headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


# --- Session Endpoint Tests ---


def test_create_session(client: TestClient, mock_db: AsyncMock) -> None:
    """Verify session creation returns expected contract schema."""
    test_user = User(
        id="usr_test123", username="researcher", role="user", is_active=True
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_user
    mock_db.execute.return_value = mock_result

    token = create_test_token("researcher")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "title": "Флотация медно-никелевой руды",
        "constraints": "Бюджет 1 млн руб.",
        "weights": {"novelty": 1.0, "feasibility": 2.0},
    }

    response = client.post("/api/v1/sessions", json=payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED

    json_data = response.json()
    assert "id" in json_data
    assert json_data["title"] == "Флотация медно-никелевой руды"
    assert json_data["status"] == "created"


def test_list_sessions(client: TestClient, mock_db: AsyncMock) -> None:
    """Verify listing sessions for authenticated user."""
    test_user = User(
        id="usr_test123", username="researcher", role="user", is_active=True
    )
    session_1 = SessionORM(
        id="sess_001",
        user_id="usr_test123",
        title="Session 1",
        status="done",
        created_at=datetime.datetime.now(datetime.UTC),
        updated_at=datetime.datetime.now(datetime.UTC),
    )

    mock_result = MagicMock()
    # First lookup returns user, second (scalars().all()) returns sessions list
    mock_result.scalar_one_or_none.return_value = test_user
    mock_result.scalars.return_value.all.return_value = [session_1]
    mock_db.execute.return_value = mock_result

    token = create_test_token("researcher")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/sessions", headers=headers)
    assert response.status_code == status.HTTP_200_OK

    json_data = response.json()
    assert json_data["total"] == 1
    assert json_data["items"][0]["title"] == "Session 1"


# --- Message and Task trigger Tests ---


def test_submit_message_triggers_celery(
    client: TestClient, mock_db: AsyncMock, mocker: MagicMock
) -> None:
    """Verify enqueuing messages registers records and enqueues Celery task."""
    test_user = User(
        id="usr_test123", username="researcher", role="user", is_active=True
    )
    session_1 = SessionORM(
        id="sess_001",
        user_id="usr_test123",
        title="Session 1",
        status="created",
    )

    # Setup database mocks
    mock_result = MagicMock()
    # 1st call: user verify; 2nd call: session check; 3rd call: iteration count
    mock_result.scalar_one_or_none.side_effect = [test_user, session_1]
    mock_result.scalar.return_value = 0  # iteration count = 0
    mock_db.execute.return_value = mock_result

    # Mock Celery client
    mock_task = MagicMock()
    mock_task.id = "task_uuid_12345"
    mock_send = mocker.patch(
        "src.api.routes.sessions.send_process_message_task", return_value=mock_task
    )

    token = create_test_token("researcher")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/api/v1/sessions/sess_001/messages",
        data={"content": "Каковы оптимальные реагентные режимы?"},
        headers=headers,
    )
    assert response.status_code == status.HTTP_202_ACCEPTED

    json_data = response.json()
    assert "message_id" in json_data
    assert json_data["task_id"] == "task_uuid_12345"
    assert json_data["status"] == "queued"

    mock_send.assert_called_once()


# --- Results & Graph Endpoint Tests ---


def test_get_results_not_ready_returns_202(
    client: TestClient, mock_db: AsyncMock
) -> None:
    """Verify getting result while processing yields 202 status."""
    test_user = User(
        id="usr_test123", username="researcher", role="user", is_active=True
    )
    message_orm = MessageORM(
        id="msg_001",
        session_id="sess_001",
        role="system",
        content="",
        status="processing",
        task_id="task_123",
    )

    mock_result = MagicMock()
    # 1. user validation
    # 2. session check
    # 3. pipeline result query (None)
    # 4. message query
    mock_result.scalar_one_or_none.side_effect = [
        test_user,
        SessionORM(),
        None,
        message_orm,
    ]
    mock_db.execute.return_value = mock_result

    token = create_test_token("researcher")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/sessions/sess_001/results/msg_001", headers=headers)
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json()["status"] == "processing"


def test_get_results_ready_returns_data(client: TestClient, mock_db: AsyncMock) -> None:
    """Verify getting ready result outputs complete JSON response."""
    test_user = User(
        id="usr_test123", username="researcher", role="user", is_active=True
    )
    pipeline_result = PipelineResultORM(
        id=1,
        session_id="sess_001",
        message_id="msg_001",
        hypothesis_json=json.dumps(
            {
                "title": "Добавка ниобия",
                "problem": "Повышение жаропрочности",
                "hypothesis": "Добавка 0.3% ниобия",
                "expected_effect": "Повышение на 15%",
                "risks": [],
                "feasibility_score": 7.0,
                "novelty_score": 6.0,
                "effect_score": 8.0,
                "risk_score": 3.0,
                "evidence_sources": [],
                "supporting_nodes": [],
                "source_chunks": [],
            }
        ),
        review_json=json.dumps(
            {
                "hypothesis_id": " Добавка ниобия",
                "scores": {},
                "comments": {},
                "verdict": "accept",
                "suggestions": [],
            }
        ),
        graph_json=json.dumps({"nodes": [], "edges": []}),
        trace_json=json.dumps(
            {
                "session_id": "sess_001",
                "iteration": 0,
                "chunks_used": [],
                "tables_queried": [],
                "history_cases_used": [],
            }
        ),
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.side_effect = [
        test_user,
        SessionORM(),
        pipeline_result,
    ]
    mock_db.execute.return_value = mock_result

    token = create_test_token("researcher")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/sessions/sess_001/results/msg_001", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "done"
    assert response.json()["hypothesis"]["title"] == "Добавка ниобия"
