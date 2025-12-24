"""Tests for interview state model."""
import pytest
from datetime import datetime
from backend.models.interview import InterviewState
from models.job import Job


def test_interview_state_creation():
    """Test that InterviewState can be created with required fields."""
    job = Job(
        id="job_1",
        title="Software Engineer",
        description="Build software",
        department="Engineering",
        location="Remote",
        requirements=["Python"]
    )
    
    state = InterviewState(
        session_id="test-session-123",
        job_id="job_1",
        job=job,
        conversation_history=[],
        current_question="What is your experience?",
        current_question_number=1,
        started_at=datetime.now(),
        ended_at=None,
        is_complete=False
    )
    
    assert state["session_id"] == "test-session-123"
    assert state["job_id"] == "job_1"
    assert state["job"] == job
    assert state["conversation_history"] == []
    assert state["current_question"] == "What is your experience?"
    assert state["current_question_number"] == 1
    assert state["is_complete"] is False
    assert state["ended_at"] is None


def test_interview_state_with_conversation_history():
    """Test InterviewState with conversation history."""
    job = Job(
        id="job_1",
        title="Engineer",
        description="Build",
        department="Eng",
        location="Remote",
        requirements=["Python"]
    )
    
    history = [
        {
            "question": "Question 1?",
            "answer": "Answer 1",
            "question_number": 1
        }
    ]
    
    state = InterviewState(
        session_id="test-123",
        job_id="job_1",
        job=job,
        conversation_history=history,
        current_question="Question 2?",
        current_question_number=2,
        started_at=datetime.now(),
        ended_at=None,
        is_complete=False
    )
    
    assert len(state["conversation_history"]) == 1
    assert state["conversation_history"][0]["question"] == "Question 1?"
    assert state["conversation_history"][0]["answer"] == "Answer 1"
    assert state["current_question_number"] == 2


def test_interview_state_completed():
    """Test InterviewState when interview is completed."""
    job = Job(
        id="job_1",
        title="Engineer",
        description="Build",
        department="Eng",
        location="Remote",
        requirements=["Python"]
    )
    
    ended_time = datetime.now()
    state = InterviewState(
        session_id="test-123",
        job_id="job_1",
        job=job,
        conversation_history=[],
        current_question=None,
        current_question_number=6,
        started_at=datetime.now(),
        ended_at=ended_time,
        is_complete=True
    )
    
    assert state["is_complete"] is True
    assert state["ended_at"] == ended_time
    assert state["current_question"] is None

