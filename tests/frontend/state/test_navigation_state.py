"""Tests for navigation state management."""
from unittest.mock import MagicMock

import pytest


def test_initialize_navigation_state_sets_defaults(mocker):
    """Test that initialize_navigation_state sets all navigation state keys with correct defaults."""
    mock_st = mocker.patch('frontend.state.navigation_state.st')
    mock_st.session_state = {}
    
    from frontend.state.navigation_state import initialize_navigation_state
    
    initialize_navigation_state()
    
    assert mock_st.session_state["current_page"] == "job_listing"
    assert mock_st.session_state["selected_job_id"] is None
    assert mock_st.session_state["completed_session_id"] is None
    assert mock_st.session_state["completed_job_id"] is None


def test_initialize_navigation_state_does_not_overwrite_existing(mocker):
    """Test that initialize_navigation_state doesn't overwrite existing state values."""
    mock_st = mocker.patch('frontend.state.navigation_state.st')
    mock_st.session_state = {
        "current_page": "interview_room",
        "selected_job_id": "job_1",
        "completed_session_id": "session_123",
        "completed_job_id": "job_2",
    }
    
    from frontend.state.navigation_state import initialize_navigation_state
    
    initialize_navigation_state()
    
    # State should remain unchanged
    assert mock_st.session_state["current_page"] == "interview_room"
    assert mock_st.session_state["selected_job_id"] == "job_1"
    assert mock_st.session_state["completed_session_id"] == "session_123"
    assert mock_st.session_state["completed_job_id"] == "job_2"


def test_initialize_navigation_state_initializes_partial_state(mocker):
    """Test that initialize_navigation_state initializes only missing keys."""
    mock_st = mocker.patch('frontend.state.navigation_state.st')
    mock_st.session_state = {
        "current_page": "interview_room",
        # Missing other keys
    }
    
    from frontend.state.navigation_state import initialize_navigation_state
    
    initialize_navigation_state()
    
    assert mock_st.session_state["current_page"] == "interview_room"  # Unchanged
    assert mock_st.session_state["selected_job_id"] is None  # Initialized
    assert mock_st.session_state["completed_session_id"] is None  # Initialized
    assert mock_st.session_state["completed_job_id"] is None  # Initialized

