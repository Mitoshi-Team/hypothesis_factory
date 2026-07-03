"""Integration tests for the API Gateway service endpoints."""

from fastapi import status
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_health_check() -> None:
    """Test that the health check endpoint returns 200 OK and expected format."""
    response = client.get("/api/v1/health")
    assert response.status_code == status.HTTP_200_OK

    json_data = response.json()
    assert json_data["status"] == "ok"
    assert json_data["environment"] == "test"
    assert "timestamp" in json_data
    assert "version" in json_data


def test_generate_hypothesis_success() -> None:
    """Test generating a scientific hypothesis successfully."""
    payload = {
        "problem_statement": "снизить потери никеля в хвостах флотации",
        "constraints": ["ограничение по бюджету", "экологический регламент"],
        "knowledge_base_ids": ["doc_001", "doc_002"],
    }
    response = client.post("/api/v1/hypotheses", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    json_data = response.json()
    assert json_data["id"] == "hyp_001"
    assert "снизить потери никеля в хвостах флотации" in json_data["formulation"]
    assert "scientific_basis" in json_data
    assert json_data["novelty"] == 3
    assert "technical" in json_data["risks"]
    assert "verification_plan" in json_data
    assert len(json_data["verification_plan"]["experiments"]) > 0
    assert json_data["score"] == 4.25


def test_generate_hypothesis_validation_error() -> None:
    """Test that sending invalid payload triggers the custom validation handler."""
    # problem_statement is missing (required)
    payload = {
        "constraints": ["no budget"],
    }
    response = client.post("/api/v1/hypotheses", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    json_data = response.json()
    assert "error" in json_data
    error_detail = json_data["error"]
    assert error_detail["code"] == "VALIDATION_ERROR"
    assert error_detail["message"] == "Request validation failed."
    assert "body.problem_statement" in error_detail["details"]
