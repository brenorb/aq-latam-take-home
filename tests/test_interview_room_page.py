"""Tests for interview room page."""
import pytest
from unittest.mock import MagicMock
from models.job import Job


def test_render_interview_room_initializes_state(mocker):
    """Test that render_interview_room initializes interview state via get_interview_state."""
    mock_st = mocker.patch('frontend.pages.interview_room.st')
    mock_st.session_state = {}
    mock_st.title = MagicMock()
    mock_st.write = MagicMock()
    mock_st.expander = MagicMock(return_value=MagicMock())
    mock_st.subheader = MagicMock()
    mock_st.divider = MagicMock()
    def columns_side_effect(sizes):
        if len(sizes) == 2:
            return [MagicMock(), MagicMock()]
        elif len(sizes) == 3:
            return [MagicMock(), MagicMock(), MagicMock()]
        return [MagicMock()] * len(sizes)
    mock_st.columns = MagicMock(side_effect=columns_side_effect)
    mock_st.button = MagicMock(return_value=False)
    mock_st.rerun = MagicMock()
    
    # Mock components
    mocker.patch('frontend.pages.interview_room.render_question_display')
    mocker.patch('frontend.pages.interview_room.render_answer_input')
    mocker.patch('frontend.pages.interview_room.render_conversation_history')
    
    # Mock state getter
    mock_get_interview_state = mocker.patch(
        'frontend.pages.interview_room.get_interview_state',
        return_value={
            "interview_started": False,
            "session_id": None,
            "conversation_history": [],
            "current_question": None,
            "question_number": 0,
            "interview_complete": False,
        }
    )
    
    job = Job(
        id="job_1",
        title="Software Engineer",
        description="Build amazing software",
        department="Engineering",
        location="Remote",
        requirements=["Python"]
    )
    
    from frontend.pages.interview_room import render_interview_room
    render_interview_room(job)
    
    # Verify state getter was called
    mock_get_interview_state.assert_called_with("job_1")


def test_render_interview_room_calls_components(mocker):
    """Test that render_interview_room calls all component rendering functions."""
    mock_st = mocker.patch('frontend.pages.interview_room.st')
    mock_st.session_state = {}
    mock_st.title = MagicMock()
    mock_st.write = MagicMock()
    mock_st.expander = MagicMock(return_value=MagicMock())
    mock_st.subheader = MagicMock()
    mock_st.divider = MagicMock()
    def columns_side_effect(sizes):
        if len(sizes) == 2:
            return [MagicMock(), MagicMock()]
        elif len(sizes) == 3:
            return [MagicMock(), MagicMock(), MagicMock()]
        return [MagicMock()] * len(sizes)
    mock_st.columns = MagicMock(side_effect=columns_side_effect)
    mock_st.button = MagicMock(return_value=False)
    mock_st.rerun = MagicMock()
    
    # Mock components
    mock_render_question_display = mocker.patch('frontend.pages.interview_room.render_question_display')
    mock_render_answer_input = mocker.patch('frontend.pages.interview_room.render_answer_input')
    mock_render_conversation_history = mocker.patch('frontend.pages.interview_room.render_conversation_history')
    
    # Mock state getter
    mocker.patch(
        'frontend.pages.interview_room.get_interview_state',
        return_value={
            "interview_started": False,
            "session_id": None,
            "conversation_history": [],
            "current_question": None,
            "question_number": 0,
            "interview_complete": False,
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
    
    from frontend.pages.interview_room import render_interview_room
    render_interview_room(job)
    
    # Verify components were called
    assert mock_render_question_display.called
    assert mock_render_answer_input.called
    assert mock_render_conversation_history.called


def test_render_interview_room_renders_action_buttons(mocker):
    """Test that action buttons (Start Interview, End Interview) are rendered."""
    mock_st = mocker.patch('frontend.pages.interview_room.st')
    mock_st.session_state = {}
    mock_st.title = MagicMock()
    mock_st.write = MagicMock()
    mock_st.expander = MagicMock(return_value=MagicMock())
    mock_st.subheader = MagicMock()
    mock_st.divider = MagicMock()
    def columns_side_effect(sizes):
        if len(sizes) == 2:
            return [MagicMock(), MagicMock()]
        elif len(sizes) == 3:
            return [MagicMock(), MagicMock(), MagicMock()]
        return [MagicMock()] * len(sizes)
    mock_st.columns = MagicMock(side_effect=columns_side_effect)
    mock_st.button = MagicMock(return_value=False)
    mock_st.rerun = MagicMock()
    
    # Mock components
    mocker.patch('frontend.pages.interview_room.render_question_display')
    mocker.patch('frontend.pages.interview_room.render_answer_input')
    mocker.patch('frontend.pages.interview_room.render_conversation_history')
    
    # Mock state getter
    mocker.patch(
        'frontend.pages.interview_room.get_interview_state',
        return_value={
            "interview_started": False,
            "session_id": None,
            "conversation_history": [],
            "current_question": None,
            "question_number": 0,
            "interview_complete": False,
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
    
    from frontend.pages.interview_room import render_interview_room
    render_interview_room(job)
    
    # Verify buttons were called
    assert mock_st.button.called



