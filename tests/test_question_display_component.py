"""Tests for question display component."""
from unittest.mock import MagicMock

import pytest


def test_render_question_display_not_started(mocker):
    """Test that question display shows correct message when interview not started."""
    mock_st = mocker.patch('frontend.components.question_display.st')
    mock_st.subheader = MagicMock()
    mock_st.info = MagicMock()
    mock_st.markdown = MagicMock()
    mock_st.caption = MagicMock()
    mock_st.divider = MagicMock()
    mock_st.success = MagicMock()
    mock_st.warning = MagicMock()
    
    interview_state = {
        "interview_started": False,
        "interview_complete": False,
        "current_question": None,
    }
    
    from frontend.components.question_display import render_question_display
    render_question_display(interview_state)
    
    mock_st.subheader.assert_called_with("Current Question")
    mock_st.info.assert_called_with("Click 'Start Interview' to begin")


def test_render_question_display_complete(mocker):
    """Test that question display shows success message when interview complete."""
    mock_st = mocker.patch('frontend.components.question_display.st')
    mock_st.subheader = MagicMock()
    mock_st.info = MagicMock()
    mock_st.markdown = MagicMock()
    mock_st.caption = MagicMock()
    mock_st.divider = MagicMock()
    mock_st.success = MagicMock()
    mock_st.warning = MagicMock()
    
    interview_state = {
        "interview_started": True,
        "interview_complete": True,
        "current_question": None,
    }
    
    from frontend.components.question_display import render_question_display
    render_question_display(interview_state)
    
    mock_st.success.assert_called_with("✅ Interview Complete!")
    assert mock_st.info.called


def test_render_question_display_current_question(mocker):
    """Test that question display shows question with styling when current question exists."""
    mock_st = mocker.patch('frontend.components.question_display.st')
    mock_st.subheader = MagicMock()
    mock_st.info = MagicMock()
    mock_st.markdown = MagicMock()
    mock_st.caption = MagicMock()
    mock_st.divider = MagicMock()
    mock_st.success = MagicMock()
    mock_st.warning = MagicMock()
    
    interview_state = {
        "interview_started": True,
        "interview_complete": False,
        "current_question": "What is your experience with Python?",
    }
    
    from frontend.components.question_display import render_question_display
    render_question_display(interview_state)
    
    # Should call markdown with HTML containing the question
    assert mock_st.markdown.called
    call_args = mock_st.markdown.call_args[0][0]
    assert "What is your experience with Python?" in call_args
    assert "unsafe_allow_html=True" in str(mock_st.markdown.call_args)
    mock_st.caption.assert_called_with("Please provide your answer below")


def test_render_question_display_loading(mocker):
    """Test that question display shows loading warning when started but no question."""
    mock_st = mocker.patch('frontend.components.question_display.st')
    mock_st.subheader = MagicMock()
    mock_st.info = MagicMock()
    mock_st.markdown = MagicMock()
    mock_st.caption = MagicMock()
    mock_st.divider = MagicMock()
    mock_st.success = MagicMock()
    mock_st.warning = MagicMock()
    
    interview_state = {
        "interview_started": True,
        "interview_complete": False,
        "current_question": None,
    }
    
    from frontend.components.question_display import render_question_display
    render_question_display(interview_state)
    
    mock_st.warning.assert_called_with("Loading question...")


def test_render_question_display_empty_state(mocker):
    """Test that question display handles empty state."""
    mock_st = mocker.patch('frontend.components.question_display.st')
    mock_st.subheader = MagicMock()
    mock_st.info = MagicMock()
    mock_st.markdown = MagicMock()
    mock_st.caption = MagicMock()
    mock_st.divider = MagicMock()
    mock_st.success = MagicMock()
    mock_st.warning = MagicMock()
    
    interview_state = {
        "interview_started": False,
        "interview_complete": False,
        "current_question": None,
    }
    
    from frontend.components.question_display import render_question_display
    render_question_display(interview_state)
    
    # Should show info message for not started
    mock_st.info.assert_called_with("Click 'Start Interview' to begin")

