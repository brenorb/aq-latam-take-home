"""Tests for interview results page."""
import pytest
from unittest.mock import MagicMock
from models.job import Job
from api_client import APIError


def test_render_interview_results_fetches_session(mocker):
    """Test that render_interview_results fetches session data via get_session."""
    mock_st = mocker.patch('frontend.pages.interview_results.st')
    mock_st.session_state = {}
    mock_st.title = MagicMock()
    mock_st.info = MagicMock()
    mock_st.divider = MagicMock()
    mock_st.header = MagicMock()
    mock_st.markdown = MagicMock()
    mock_st.metric = MagicMock()
    mock_st.subheader = MagicMock()
    mock_st.expander = MagicMock(return_value=MagicMock())
    mock_st.json = MagicMock()
    mock_st.button = MagicMock(return_value=False)
    mock_st.rerun = MagicMock()
    mock_st.spinner = MagicMock(return_value=MagicMock())
    mock_st.error = MagicMock()
    
    mock_get_session = mocker.patch(
        'frontend.pages.interview_results.get_session',
        return_value={
            "session_id": "test-session-123",
            "started_at": "2024-01-01T00:00:00",
            "ended_at": "2024-01-01T00:30:00",
            "conversation_history": []
        }
    )
    
    mocker.patch(
        'frontend.pages.interview_results.get_evaluation',
        return_value={
            "overall_score": 85.0,
            "strengths": ["Good communication"],
            "concerns": []
        }
    )
    
    job = Job(
        id="job_1",
        title="Engineer",
        description="Build",
        department="Eng",
        location="Remote",
        requirements=["Python"]
    )
    
    from frontend.pages.interview_results import render_interview_results
    render_interview_results("test-session-123", job)
    
    # Verify get_session was called
    mock_get_session.assert_called_with("test-session-123")


def test_render_interview_results_displays_session_info(mocker):
    """Test that session info is displayed."""
    mock_st = mocker.patch('frontend.pages.interview_results.st')
    mock_st.session_state = {}
    mock_st.title = MagicMock()
    mock_st.info = MagicMock()
    mock_st.divider = MagicMock()
    mock_st.header = MagicMock()
    mock_st.markdown = MagicMock()
    mock_st.metric = MagicMock()
    mock_st.subheader = MagicMock()
    mock_st.expander = MagicMock(return_value=MagicMock())
    mock_st.json = MagicMock()
    mock_st.button = MagicMock(return_value=False)
    mock_st.rerun = MagicMock()
    mock_st.spinner = MagicMock(return_value=MagicMock())
    mock_st.error = MagicMock()
    
    mocker.patch(
        'frontend.pages.interview_results.get_session',
        return_value={
            "session_id": "test-session-123",
            "started_at": "2024-01-01T00:00:00",
            "ended_at": "2024-01-01T00:30:00",
            "conversation_history": []
        }
    )
    
    mocker.patch(
        'frontend.pages.interview_results.get_evaluation',
        return_value={
            "overall_score": 85.0,
            "strengths": [],
            "concerns": []
        }
    )
    
    job = Job(
        id="job_1",
        title="Engineer",
        description="Build",
        department="Eng",
        location="Remote",
        requirements=["Python"]
    )
    
    from frontend.pages.interview_results import render_interview_results
    render_interview_results("test-session-123", job)
    
    # Verify info was displayed
    assert mock_st.info.called


def test_render_interview_results_displays_evaluation(mocker):
    """Test that evaluation section displays score, strengths, concerns."""
    mock_st = mocker.patch('frontend.pages.interview_results.st')
    mock_st.session_state = {}
    mock_st.title = MagicMock()
    mock_st.info = MagicMock()
    mock_st.divider = MagicMock()
    mock_st.header = MagicMock()
    mock_st.markdown = MagicMock()
    mock_st.metric = MagicMock()
    mock_st.subheader = MagicMock()
    mock_st.expander = MagicMock(return_value=MagicMock())
    mock_st.json = MagicMock()
    mock_st.button = MagicMock(return_value=False)
    mock_st.rerun = MagicMock()
    mock_st.spinner = MagicMock(return_value=MagicMock())
    mock_st.error = MagicMock()
    
    mocker.patch(
        'frontend.pages.interview_results.get_session',
        return_value={
            "session_id": "test-session-123",
            "started_at": "2024-01-01T00:00:00",
            "ended_at": "2024-01-01T00:30:00",
            "conversation_history": []
        }
    )
    
    mocker.patch(
        'frontend.pages.interview_results.get_evaluation',
        return_value={
            "overall_score": 85.0,
            "strengths": ["Good communication", "Technical skills"],
            "concerns": ["Could improve time management"]
        }
    )
    
    job = Job(
        id="job_1",
        title="Engineer",
        description="Build",
        department="Eng",
        location="Remote",
        requirements=["Python"]
    )
    
    from frontend.pages.interview_results import render_interview_results
    render_interview_results("test-session-123", job)
    
    # Verify evaluation was displayed
    assert mock_st.metric.called
    assert mock_st.subheader.called


def test_render_interview_results_handles_api_error_session(mocker):
    """Test that APIError for session fetch is handled correctly."""
    mock_st = mocker.patch('frontend.pages.interview_results.st')
    mock_st.session_state = {}
    mock_st.title = MagicMock()
    mock_st.info = MagicMock()
    mock_st.divider = MagicMock()
    mock_st.header = MagicMock()
    mock_st.markdown = MagicMock()
    mock_st.metric = MagicMock()
    mock_st.subheader = MagicMock()
    mock_st.expander = MagicMock(return_value=MagicMock())
    mock_st.json = MagicMock()
    mock_st.button = MagicMock(return_value=False)
    mock_st.rerun = MagicMock()
    mock_st.spinner = MagicMock(return_value=MagicMock())
    mock_st.error = MagicMock()
    
    mocker.patch(
        'frontend.pages.interview_results.get_session',
        side_effect=APIError("Session not found")
    )
    
    job = Job(
        id="job_1",
        title="Engineer",
        description="Build",
        department="Eng",
        location="Remote",
        requirements=["Python"]
    )
    
    from frontend.pages.interview_results import render_interview_results
    render_interview_results("test-session-123", job)
    
    # Verify error was displayed
    assert mock_st.error.called

