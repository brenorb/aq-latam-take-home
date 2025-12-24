"""Tests for interview state management."""
import os
from unittest.mock import MagicMock, patch

import pytest


def test_get_interview_state_initializes_defaults(mocker):
    """Test that get_interview_state initializes state with correct default values."""
    mock_st = mocker.patch('frontend.state.interview_state.st')
    mock_st.session_state = {}
    
    with patch.dict(os.environ, {}, clear=True):
        from frontend.state.interview_state import get_interview_state
        
        state = get_interview_state("job_1")
        
        assert state["interview_started"] is False
        assert state["session_id"] is None
        assert state["conversation_history"] == []
        assert state["current_question"] is None
        assert state["question_number"] == 0
        assert state["interview_complete"] is False
        assert state["answer_text"] == ""
        assert state["debug_mode"] is False
        assert state["recording_state"] == "idle"
        assert state["transcribed_text"] == ""
        assert state["transcription_error"] is None


def test_get_interview_state_uses_existing_state(mocker):
    """Test that get_interview_state returns existing state if it exists."""
    mock_st = mocker.patch('frontend.state.interview_state.st')
    state_key = "interview_state_job_1"
    existing_state = {
        "interview_started": True,
        "session_id": "test-session",
        "conversation_history": [{"question": "Q1", "answer": "A1"}],
        "current_question": "Q2",
        "question_number": 2,
        "interview_complete": False,
        "answer_text": "",
        "debug_mode": False,
        "recording_state": "idle",
        "transcribed_text": "",
        "transcription_error": None,
    }
    mock_st.session_state = {state_key: existing_state}
    
    from frontend.state.interview_state import get_interview_state
    
    state = get_interview_state("job_1")
    
    assert state == existing_state
    assert state["interview_started"] is True
    assert state["session_id"] == "test-session"


def test_get_interview_state_generates_correct_key(mocker):
    """Test that get_interview_state generates state key correctly."""
    mock_st = mocker.patch('frontend.state.interview_state.st')
    mock_st.session_state = {}
    
    from frontend.state.interview_state import get_interview_state
    
    get_interview_state("job_1")
    
    assert "interview_state_job_1" in mock_st.session_state
    
    get_interview_state("job_2")
    
    assert "interview_state_job_2" in mock_st.session_state


def test_get_interview_state_debug_mode_from_env(mocker):
    """Test that debug_mode is initialized from environment variable."""
    mock_st = mocker.patch('frontend.state.interview_state.st')
    mock_st.session_state = {}
    
    with patch.dict(os.environ, {"DEBUG_MODE": "true"}):
        from frontend.state.interview_state import get_interview_state
        
        state = get_interview_state("job_1")
        
        assert state["debug_mode"] is True
    
    with patch.dict(os.environ, {"DEBUG_MODE": "1"}):
        from frontend.state.interview_state import get_interview_state
        
        state = get_interview_state("job_2")
        
        assert state["debug_mode"] is True
    
    with patch.dict(os.environ, {}, clear=True):
        from frontend.state.interview_state import get_interview_state
        
        state = get_interview_state("job_3")
        
        assert state["debug_mode"] is False

