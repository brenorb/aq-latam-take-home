"""Tests for interview service."""
import pytest
from unittest.mock import MagicMock, patch
from api_client import APIError


def test_start_interview_handler_success(mocker):
    """Test that start_interview_handler successfully starts interview and updates state."""
    mock_st = mocker.patch('frontend.services.interview_service.st')
    mock_st.session_state = {}
    mock_st.rerun = MagicMock()
    
    mock_start_interview = mocker.patch(
        'frontend.services.interview_service.start_interview',
        return_value={
            "session_id": "test-session-123",
            "question": "What is your experience?",
            "question_number": 1,
            "conversation_history": []
        }
    )
    
    interview_state = {
        "interview_started": False,
        "session_id": None,
        "conversation_history": [],
        "current_question": None,
        "question_number": 0,
        "interview_complete": False,
    }
    
    from frontend.services.interview_service import start_interview_handler
    start_interview_handler("job_1", interview_state)
    
    assert interview_state["interview_started"] is True
    assert interview_state["session_id"] == "test-session-123"
    assert interview_state["current_question"] == "What is your experience?"
    assert interview_state["question_number"] == 1
    assert mock_start_interview.called
    assert mock_st.rerun.called


def test_start_interview_handler_api_error(mocker):
    """Test that start_interview_handler handles APIError correctly."""
    mock_st = mocker.patch('frontend.services.interview_service.st')
    mock_st.session_state = {}
    mock_st.rerun = MagicMock()
    mock_st.error = MagicMock()
    
    mocker.patch(
        'frontend.services.interview_service.start_interview',
        side_effect=APIError("API error: Job not found")
    )
    
    interview_state = {
        "interview_started": False,
        "session_id": None,
    }
    
    from frontend.services.interview_service import start_interview_handler
    start_interview_handler("job_1", interview_state)
    
    # State should not be updated on error
    assert interview_state["interview_started"] is False
    assert mock_st.error.called


def test_submit_answer_handler_success(mocker):
    """Test that submit_answer_handler successfully submits answer and updates state."""
    mock_st = mocker.patch('frontend.services.interview_service.st')
    mock_st.session_state = {"selected_job_id": "job_1"}
    mock_st.rerun = MagicMock()
    
    mock_submit_answer = mocker.patch(
        'frontend.services.interview_service.submit_answer',
        return_value={
            "question": "Next question?",
            "question_number": 2,
            "interview_complete": False,
            "conversation_history": [
                {"question": "Q1", "answer": "A1", "question_number": 1}
            ]
        }
    )
    
    interview_state = {
        "session_id": "test-session-123",
        "conversation_history": [],
        "current_question": "Q1",
        "question_number": 1,
        "interview_complete": False,
    }
    
    from frontend.services.interview_service import submit_answer_handler
    submit_answer_handler("test-session-123", "My answer", interview_state, "job_1")
    
    assert interview_state["current_question"] == "Next question?"
    assert interview_state["question_number"] == 2
    assert len(interview_state["conversation_history"]) == 1
    assert mock_submit_answer.called
    assert mock_st.rerun.called


def test_submit_answer_handler_interview_complete(mocker):
    """Test that submit_answer_handler navigates to results when interview complete."""
    mock_st = mocker.patch('frontend.services.interview_service.st')
    mock_st.session_state = {}
    mock_st.rerun = MagicMock()
    
    mocker.patch(
        'frontend.services.interview_service.submit_answer',
        return_value={
            "question": None,
            "question_number": 3,
            "interview_complete": True,
            "conversation_history": [
                {"question": "Q1", "answer": "A1", "question_number": 1},
                {"question": "Q2", "answer": "A2", "question_number": 2},
            ]
        }
    )
    
    interview_state = {
        "session_id": "test-session-123",
        "conversation_history": [],
        "current_question": "Q2",
        "question_number": 2,
        "interview_complete": False,
    }
    
    from frontend.services.interview_service import submit_answer_handler
    submit_answer_handler("test-session-123", "Final answer", interview_state, "job_1")
    
    assert interview_state["interview_complete"] is True
    assert mock_st.session_state["completed_session_id"] == "test-session-123"
    assert mock_st.session_state["completed_job_id"] == "job_1"
    assert mock_st.session_state["current_page"] == "interview_results"
    assert mock_st.rerun.called


def test_submit_answer_handler_api_error(mocker):
    """Test that submit_answer_handler handles APIError correctly."""
    mock_st = mocker.patch('frontend.services.interview_service.st')
    mock_st.session_state = {}
    mock_st.rerun = MagicMock()
    mock_st.error = MagicMock()
    
    mocker.patch(
        'frontend.services.interview_service.submit_answer',
        side_effect=APIError("API error: Session not found")
    )
    
    interview_state = {
        "session_id": "test-session-123",
        "conversation_history": [],
        "current_question": "Q1",
        "question_number": 1,
        "interview_complete": False,
    }
    
    from frontend.services.interview_service import submit_answer_handler
    submit_answer_handler("test-session-123", "My answer", interview_state)
    
    # State should not be updated on error
    assert interview_state["current_question"] == "Q1"
    assert mock_st.error.called


def test_submit_answer_handler_none_session_id(mocker):
    """Test that submit_answer_handler returns early when session_id is None."""
    mock_st = mocker.patch('frontend.services.interview_service.st')
    mock_st.session_state = {}
    mock_st.error = MagicMock()
    
    mock_submit_answer = mocker.patch(
        'frontend.services.interview_service.submit_answer'
    )
    
    interview_state = {
        "session_id": None,
        "conversation_history": [],
        "current_question": "Q1",
        "question_number": 1,
        "interview_complete": False,
    }
    
    from frontend.services.interview_service import submit_answer_handler
    submit_answer_handler(None, "My answer", interview_state)
    
    # Should not call API
    assert not mock_submit_answer.called
    # Should show error message
    assert mock_st.error.called
    # State should not be updated
    assert interview_state["current_question"] == "Q1"


def test_end_interview_handler_success(mocker):
    """Test that end_interview_handler successfully ends interview and updates navigation."""
    mock_st = mocker.patch('frontend.services.interview_service.st')
    mock_st.session_state = {}
    mock_st.rerun = MagicMock()
    
    mock_end_interview = mocker.patch(
        'frontend.services.interview_service.end_interview',
        return_value={"session_id": "test-session-123", "message": "Interview ended"}
    )
    
    interview_state = {
        "session_id": "test-session-123",
    }
    
    from frontend.services.interview_service import end_interview_handler
    end_interview_handler("test-session-123", interview_state, "job_1")
    
    assert mock_end_interview.called
    assert mock_st.session_state["completed_session_id"] == "test-session-123"
    assert mock_st.session_state["completed_job_id"] == "job_1"
    assert mock_st.session_state["current_page"] == "interview_results"
    assert mock_st.rerun.called


def test_end_interview_handler_api_error(mocker):
    """Test that end_interview_handler handles APIError correctly."""
    mock_st = mocker.patch('frontend.services.interview_service.st')
    mock_st.session_state = {}
    mock_st.rerun = MagicMock()
    mock_st.error = MagicMock()
    
    mocker.patch(
        'frontend.services.interview_service.end_interview',
        side_effect=APIError("API error: Session not found")
    )
    
    interview_state = {
        "session_id": "test-session-123",
    }
    
    from frontend.services.interview_service import end_interview_handler
    end_interview_handler("test-session-123", interview_state, "job_1")
    
    assert mock_st.error.called
    # Should still navigate to results page with valid session_id
    assert mock_st.session_state["completed_session_id"] == "test-session-123"
    assert mock_st.session_state["completed_job_id"] == "job_1"
    assert mock_st.session_state["current_page"] == "interview_results"


def test_end_interview_handler_none_session_id(mocker):
    """Test that end_interview_handler returns early when session_id is None."""
    mock_st = mocker.patch('frontend.services.interview_service.st')
    mock_st.session_state = {}
    mock_st.error = MagicMock()
    
    mock_end_interview = mocker.patch(
        'frontend.services.interview_service.end_interview'
    )
    
    interview_state = {
        "session_id": None,
    }
    
    from frontend.services.interview_service import end_interview_handler
    end_interview_handler(None, interview_state)
    
    # Should not call API
    assert not mock_end_interview.called
    # Should show error message
    assert mock_st.error.called
    # Should not navigate
    assert "completed_session_id" not in mock_st.session_state
    assert mock_st.session_state.get("current_page") != "interview_results"
