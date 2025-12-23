"""Tests for interview service."""
import pytest
from datetime import datetime, timezone
from backend.services.interview_service import InterviewService
from models.job import Job, load_jobs


def test_start_interview():
    """Test starting an interview creates session and returns question."""
    service = InterviewService()
    
    result = service.start_interview("job_1")
    
    assert "session_id" in result
    assert "question" in result
    assert "question_number" in result
    assert "conversation_history" in result
    assert result["question_number"] == 1
    assert isinstance(result["question"], str)
    assert len(result["question"]) > 0
    assert isinstance(result["conversation_history"], list)
    assert len(result["conversation_history"]) == 0  # Empty at start


def test_start_interview_generates_unique_session_ids():
    """Test that each interview gets a unique session ID."""
    service = InterviewService()
    
    result1 = service.start_interview("job_1")
    result2 = service.start_interview("job_1")
    
    assert result1["session_id"] != result2["session_id"]


def test_start_interview_stores_state():
    """Test that interview state is stored after starting."""
    service = InterviewService()
    
    result = service.start_interview("job_1")
    session_id = result["session_id"]
    
    # Verify state exists
    assert session_id in service._interviews
    state = service._interviews[session_id]
    assert state["job_id"] == "job_1"
    assert state["current_question_number"] == 1
    assert state["is_complete"] is False


def test_submit_answer():
    """Test submitting an answer returns next question."""
    service = InterviewService()
    
    start_result = service.start_interview("job_1")
    session_id = start_result["session_id"]
    first_question = start_result["question"]
    
    answer_result = service.submit_answer(session_id, "I am interested because...")
    
    assert "question" in answer_result
    assert "question_number" in answer_result
    assert "interview_complete" in answer_result
    assert "conversation_history" in answer_result
    assert answer_result["question_number"] == 2
    assert answer_result["interview_complete"] is False
    assert isinstance(answer_result["question"], str)
    assert isinstance(answer_result["conversation_history"], list)
    assert len(answer_result["conversation_history"]) == 1
    assert answer_result["conversation_history"][0]["question"] == first_question
    assert answer_result["conversation_history"][0]["answer"] == "I am interested because..."
    assert answer_result["conversation_history"][0]["question_number"] == 1


def test_submit_answer_adds_to_conversation_history():
    """Test that submitting answer adds Q/A pair to history."""
    service = InterviewService()
    
    start_result = service.start_interview("job_1")
    session_id = start_result["session_id"]
    first_question = start_result["question"]
    
    service.submit_answer(session_id, "My answer")
    
    state = service._interviews[session_id]
    assert len(state["conversation_history"]) == 1
    assert state["conversation_history"][0]["question"] == first_question
    assert state["conversation_history"][0]["answer"] == "My answer"
    assert state["conversation_history"][0]["question_number"] == 1


def test_submit_answer_completes_after_max_questions():
    """Test that interview completes after max questions."""
    service = InterviewService()
    service.max_questions = 3  # Set lower for testing
    
    start_result = service.start_interview("job_1")
    session_id = start_result["session_id"]
    
    # Submit answers until complete (start at Q1, need 2 more to reach Q3, then one more to exceed)
    result1 = service.submit_answer(session_id, "Answer 1")  # Now at Q2
    assert result1["interview_complete"] is False
    
    result2 = service.submit_answer(session_id, "Answer 2")  # Now at Q3
    assert result2["interview_complete"] is False
    
    result3 = service.submit_answer(session_id, "Answer 3")  # Now at Q4, exceeds max_questions=3
    assert result3["interview_complete"] is True
    assert result3["question"] is None
    assert "conversation_history" in result3
    assert len(result3["conversation_history"]) == 3  # All 3 questions answered
    assert result3["question_number"] == 3  # Last question answered


def test_submit_answer_invalid_session():
    """Test that submitting answer with invalid session raises error."""
    service = InterviewService()
    
    with pytest.raises(ValueError, match="Session not found"):
        service.submit_answer("invalid-session-id", "Answer")


def test_submit_answer_empty_answer():
    """Test that submitting empty answer raises error."""
    service = InterviewService()
    
    start_result = service.start_interview("job_1")
    session_id = start_result["session_id"]
    
    with pytest.raises(ValueError, match="Answer cannot be empty"):
        service.submit_answer(session_id, "")


def test_end_interview():
    """Test ending an interview marks it as complete."""
    service = InterviewService()
    
    start_result = service.start_interview("job_1")
    session_id = start_result["session_id"]
    
    result = service.end_interview(session_id)
    
    assert result["session_id"] == session_id
    assert "message" in result
    
    state = service._interviews[session_id]
    assert state["is_complete"] is True
    assert state["ended_at"] is not None
    # Verify timezone awareness
    assert state["started_at"].tzinfo is not None
    assert state["ended_at"].tzinfo is not None


def test_end_interview_invalid_session():
    """Test that ending interview with invalid session raises error."""
    service = InterviewService()
    
    with pytest.raises(ValueError, match="Session not found"):
        service.end_interview("invalid-session-id")


def test_interview_state_persistence():
    """Test that interview state persists across multiple operations."""
    service = InterviewService()
    
    start_result = service.start_interview("job_1")
    session_id = start_result["session_id"]
    
    # Submit multiple answers
    service.submit_answer(session_id, "Answer 1")
    service.submit_answer(session_id, "Answer 2")
    
    state = service._interviews[session_id]
    assert len(state["conversation_history"]) == 2
    assert state["current_question_number"] == 3

