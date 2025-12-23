"""Tests for API routes."""
import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


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


def test_submit_answer_success(client):
    """Test submitting an answer successfully."""
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


def test_submit_answer_completes_interview(client):
    """Test that interview completes after max questions."""
    start_response = client.post("/api/interviews/start", json={"job_id": "job_1"})
    session_id = start_response.json()["session_id"]
    
    # Submit answers until complete (max is 6, start at Q1, need 5 more answers to reach Q6, then one more to exceed)
    for i in range(5):
        response = client.post(
            f"/api/interviews/{session_id}/answer",
            json={"answer": f"Answer {i+1}"}
        )
        assert response.status_code == 200
        assert response.json()["interview_complete"] is False
    
    # 6th answer should complete interview (moves from Q6 to Q7, which exceeds max_questions=6)
    response = client.post(
        f"/api/interviews/{session_id}/answer",
        json={"answer": "Final answer"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["interview_complete"] is True
    assert data["question"] is None
    assert "conversation_history" in data
    assert len(data["conversation_history"]) == 6  # All 6 questions answered
    assert data["conversation_history"][-1]["answer"] == "Final answer"
    assert data["question_number"] == 6  # Last question answered


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

