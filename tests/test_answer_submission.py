"""Tests for answer submission functionality."""
import pytest
from unittest.mock import MagicMock
from models.job import Job


def test_answer_form_uses_form_context_manager(mocker):
    """Test that answer input uses st.form for Enter key support."""
    mock_st = mocker.patch('main.st')
    mock_st.session_state = {
        "interview_state_job_1": {
            "interview_started": True,
            "session_id": "test-session-123",
            "conversation_history": [],
            "current_question": "Question 1?",
            "question_number": 1,
            "interview_complete": False,
            "answer_text": "",
        }
    }
    mock_st.title = MagicMock()
    mock_st.write = MagicMock()
    mock_st.expander = MagicMock(return_value=MagicMock())
    mock_st.subheader = MagicMock()
    mock_st.divider = MagicMock()
    mock_st.columns = MagicMock(side_effect=lambda sizes: [MagicMock() for _ in sizes])
    mock_st.markdown = MagicMock()
    mock_st.info = MagicMock()
    mock_st.rerun = MagicMock()
    mock_st.container = MagicMock(return_value=MagicMock())
    mock_st.warning = MagicMock()
    mock_st.success = MagicMock()
    mock_st.error = MagicMock()
    
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
    
    job = Job(
        id="job_1",
        title="Engineer",
        description="Build",
        department="Eng",
        location="Remote",
        requirements=["Python"]
    )
    
    from main import render_interview_room
    render_interview_room(job)
    
    # Verify form was used (for Enter key support)
    assert mock_st.form.called
    # Verify form was called with clear_on_submit=True
    call_args = mock_st.form.call_args
    assert call_args[1].get("clear_on_submit") is True


def test_answer_form_includes_javascript_for_cmd_enter(mocker):
    """Test that JavaScript is injected for Cmd+Enter support."""
    mock_st = mocker.patch('main.st')
    mock_st.session_state = {
        "interview_state_job_1": {
            "interview_started": True,
            "session_id": "test-session-123",
            "conversation_history": [],
            "current_question": "Question 1?",
            "question_number": 1,
            "interview_complete": False,
            "answer_text": "",
        }
    }
    mock_st.title = MagicMock()
    mock_st.write = MagicMock()
    mock_st.expander = MagicMock(return_value=MagicMock())
    mock_st.subheader = MagicMock()
    mock_st.divider = MagicMock()
    mock_st.columns = MagicMock(side_effect=lambda sizes: [MagicMock() for _ in sizes])
    mock_st.markdown = MagicMock()
    mock_st.info = MagicMock()
    mock_st.rerun = MagicMock()
    mock_st.container = MagicMock(return_value=MagicMock())
    mock_st.warning = MagicMock()
    mock_st.success = MagicMock()
    mock_st.error = MagicMock()
    
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
    
    job = Job(
        id="job_1",
        title="Engineer",
        description="Build",
        department="Eng",
        location="Remote",
        requirements=["Python"]
    )
    
    from main import render_interview_room
    render_interview_room(job)
    
    # Verify JavaScript was injected for Cmd+Enter support
    assert mock_st.components.v1.html.called

