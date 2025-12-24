"""Tests for answer submission functionality."""
import pytest
from unittest.mock import MagicMock
from models.job import Job


def test_answer_form_uses_form_context_manager(mocker):
    """Test that answer input uses st.form for Enter key support."""
    mock_st = mocker.patch('frontend.components.answer_input.st')
    mock_st.subheader = MagicMock()
    mock_st.info = MagicMock()
    mock_st.button = MagicMock(return_value=False)
    
    # Mock form context manager
    mock_form = MagicMock()
    mock_form.__enter__ = MagicMock(return_value=mock_form)
    mock_form.__exit__ = MagicMock(return_value=False)
    mock_form.text_area = MagicMock(return_value="")
    mock_form.form_submit_button = MagicMock(return_value=False)
    mock_st.form = MagicMock(return_value=mock_form)
    
    # Mock components.v1.html for JavaScript injection
    mock_st.components = MagicMock()
    mock_st.components.v1 = MagicMock()
    mock_st.components.v1.html = MagicMock()
    
    # Mock audio recorder component
    mocker.patch('frontend.components.answer_input.render_audio_recorder')
    mocker.patch('frontend.components.answer_input.submit_answer_handler')
    
    job = Job(
        id="job_1",
        title="Engineer",
        description="Build",
        department="Eng",
        location="Remote",
        requirements=["Python"]
    )
    
    interview_state = {
        "interview_started": True,
        "interview_complete": False,
        "recording_state": "idle",
        "transcribed_text": "",
        "debug_mode": False,
        "session_id": "test-session-123",
    }
    
    from frontend.components.answer_input import render_answer_input
    render_answer_input(job, interview_state)
    
    # Verify form was used (for Enter key support)
    assert mock_st.form.called
    # Verify form was called with clear_on_submit=True
    call_args = mock_st.form.call_args
    assert call_args[1].get("clear_on_submit") is True


def test_answer_form_includes_javascript_for_cmd_enter(mocker):
    """Test that JavaScript is injected for Cmd+Enter support."""
    mock_st = mocker.patch('frontend.components.answer_input.st')
    mock_st.subheader = MagicMock()
    mock_st.info = MagicMock()
    mock_st.button = MagicMock(return_value=False)
    
    # Mock form context manager
    mock_form = MagicMock()
    mock_form.__enter__ = MagicMock(return_value=mock_form)
    mock_form.__exit__ = MagicMock(return_value=False)
    mock_form.text_area = MagicMock(return_value="")
    mock_form.form_submit_button = MagicMock(return_value=False)
    mock_st.form = MagicMock(return_value=mock_form)
    
    # Mock components.v1.html for JavaScript injection
    mock_st.components = MagicMock()
    mock_st.components.v1 = MagicMock()
    mock_st.components.v1.html = MagicMock()
    
    # Mock audio recorder component
    mocker.patch('frontend.components.answer_input.render_audio_recorder')
    mocker.patch('frontend.components.answer_input.submit_answer_handler')
    
    job = Job(
        id="job_1",
        title="Engineer",
        description="Build",
        department="Eng",
        location="Remote",
        requirements=["Python"]
    )
    
    interview_state = {
        "interview_started": True,
        "interview_complete": False,
        "recording_state": "idle",
        "transcribed_text": "",
        "debug_mode": False,
        "session_id": "test-session-123",
    }
    
    from frontend.components.answer_input import render_answer_input
    render_answer_input(job, interview_state)
    
    # Verify JavaScript was injected for Cmd+Enter support
    assert mock_st.components.v1.html.called
