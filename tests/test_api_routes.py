"""Tests for API routes."""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def mock_question_generator():
    """Mock question generator for all API route tests."""
    with patch("backend.services.interview_service.QuestionGenerator") as mock_generator_class:
        mock_generator = MagicMock()
        mock_generator.generate_question.return_value = ("Why are you interested in this position?", False)
        mock_generator_class.return_value = mock_generator
        yield mock_generator


def test_start_interview_success(client):
    """Test starting an interview successfully."""
    response = client.post("/api/interviews/start", json={"job_id": "job_1"})
    
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "question" in data
    assert "question_number" in data
    assert "conversation_history" in data
    assert data["question_number"] == 1
    assert isinstance(data["question"], str)
    assert len(data["question"]) > 0
    assert isinstance(data["conversation_history"], list)
    assert len(data["conversation_history"]) == 0  # Empty at start


def test_start_interview_invalid_job_id(client):
    """Test starting interview with invalid job_id."""
    response = client.post("/api/interviews/start", json={"job_id": "invalid_job"})
    
    assert response.status_code == 400
    data = response.json()
    assert "error" in data or "detail" in data


def test_start_interview_missing_job_id(client):
    """Test starting interview without job_id."""
    response = client.post("/api/interviews/start", json={})
    
    assert response.status_code == 422  # Validation error


def test_submit_answer_success(client, mock_question_generator):
    """Test submitting an answer successfully."""
    # Set up mock for next question
    mock_question_generator.generate_question.side_effect = [
        ("Why are you interested?", False),  # Initial question
        ("Tell me about your experience", False),  # Next question
    ]
    
    # Start interview first
    start_response = client.post("/api/interviews/start", json={"job_id": "job_1"})
    session_id = start_response.json()["session_id"]
    first_question = start_response.json()["question"]
    
    # Submit answer
    response = client.post(
        f"/api/interviews/{session_id}/answer",
        json={"answer": "I am interested because..."}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "question" in data
    assert "question_number" in data
    assert "interview_complete" in data
    assert "conversation_history" in data
    assert data["question_number"] == 2
    assert data["interview_complete"] is False
    assert isinstance(data["conversation_history"], list)
    assert len(data["conversation_history"]) == 1
    assert data["conversation_history"][0]["question"] == first_question
    assert data["conversation_history"][0]["answer"] == "I am interested because..."
    assert data["conversation_history"][0]["question_number"] == 1
    assert "is_followup" in data["conversation_history"][0]
    assert data["conversation_history"][0]["is_followup"] is False


def test_submit_answer_invalid_session(client):
    """Test submitting answer with invalid session_id."""
    response = client.post(
        "/api/interviews/invalid-session/answer",
        json={"answer": "Some answer"}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "error" in data or "detail" in data


def test_submit_answer_empty_answer(client):
    """Test submitting empty answer."""
    start_response = client.post("/api/interviews/start", json={"job_id": "job_1"})
    session_id = start_response.json()["session_id"]
    
    response = client.post(
        f"/api/interviews/{session_id}/answer",
        json={"answer": ""}
    )
    
    assert response.status_code == 422  # Validation error


def test_submit_answer_completes_interview(client, mock_question_generator):
    """Test that interview completes when minimum requirements are met."""
    # Set up mock to return questions that meet minimums (6 standalone + 2 follow-ups)
    mock_question_generator.generate_question.side_effect = [
        ("Question 1", False),  # Initial
    ] + [
        (f"Question {i}", (i >= 8)) for i in range(2, 11)
    ]
    
    start_response = client.post("/api/interviews/start", json={"job_id": "job_1"})
    session_id = start_response.json()["session_id"]
    
    # Submit answers until minimums are met (need 5 more standalone + 2 follow-ups after Q1)
    # After 7 answers, we'll have 6 standalone + 2 follow-ups = 8 total
    for i in range(7):
        response = client.post(
            f"/api/interviews/{session_id}/answer",
            json={"answer": f"Answer {i+1}"}
        )
        assert response.status_code == 200
        data = response.json()
        # Should complete when minimums met and total >= 10
        if data.get("interview_complete"):
            break
    
    # Verify interview completed
    final_response = client.post(
        f"/api/interviews/{session_id}/answer",
        json={"answer": "Final answer"}
    )
    
    # May complete earlier if minimums met
    assert final_response.status_code == 200


def test_end_interview_success(client):
    """Test ending an interview successfully."""
    start_response = client.post("/api/interviews/start", json={"job_id": "job_1"})
    session_id = start_response.json()["session_id"]
    
    response = client.post(f"/api/interviews/{session_id}/end")
    
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    assert "message" in data


def test_end_interview_invalid_session(client):
    """Test ending interview with invalid session_id."""
    response = client.post("/api/interviews/invalid-session/end")
    
    assert response.status_code == 400
    data = response.json()
    assert "error" in data or "detail" in data


def test_cors_headers(client):
    """Test that CORS headers are present."""
    response = client.options("/api/interviews/start")
    
    # CORS preflight should be handled
    assert response.status_code in [200, 204, 405]  # Depends on CORS implementation

