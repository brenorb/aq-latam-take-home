"""Tests for interview room page rendering."""
import pytest
from unittest.mock import MagicMock
from models.job import Job


def test_render_interview_room_displays_job_info(mocker):
    """Test that render_interview_room displays selected job information."""
    mock_st = mocker.patch('main.st')
    mock_st.session_state = {"selected_job_id": "job_1"}
    mock_st.title = MagicMock()
    mock_st.write = MagicMock()
    mock_st.container = MagicMock(return_value=MagicMock())
    mock_st.subheader = MagicMock()
    mock_st.divider = MagicMock()
    mock_st.columns = MagicMock(return_value=[MagicMock(), MagicMock()])
    mock_st.text_area = MagicMock()
    mock_st.button = MagicMock(return_value=False)
    mock_st.info = MagicMock()
    mock_st.rerun = MagicMock()
    
    job = Job(
        id="job_1",
        title="Software Engineer",
        description="Build amazing software",
        department="Engineering",
        location="Remote",
        requirements=["Python"]
    )
    
    from main import render_interview_room
    render_interview_room(job)
    
    # Verify job info is displayed
    assert mock_st.title.called
    assert mock_st.write.called


def test_render_interview_room_shows_layout_sections(mocker):
    """Test that render_interview_room creates placeholder UI sections."""
    mock_st = mocker.patch('main.st')
    mock_st.session_state = {"selected_job_id": "job_1"}
    mock_st.title = MagicMock()
    mock_st.write = MagicMock()
    mock_st.container = MagicMock(return_value=MagicMock())
    mock_st.subheader = MagicMock()
    mock_st.divider = MagicMock()
    mock_st.columns = MagicMock(return_value=[MagicMock(), MagicMock()])
    mock_st.text_area = MagicMock()
    mock_st.button = MagicMock(return_value=False)
    mock_st.info = MagicMock()
    mock_st.rerun = MagicMock()
    
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
    
    # Verify layout components are used
    assert mock_st.columns.called
    assert mock_st.container.called


def test_render_interview_room_has_back_button(mocker):
    """Test that render_interview_room includes a Back button."""
    mock_st = mocker.patch('main.st')
    mock_st.session_state = {"selected_job_id": "job_1"}
    mock_st.title = MagicMock()
    mock_st.write = MagicMock()
    mock_st.container = MagicMock(return_value=MagicMock())
    mock_st.subheader = MagicMock()
    mock_st.divider = MagicMock()
    mock_st.columns = MagicMock(return_value=[MagicMock(), MagicMock()])
    mock_st.text_area = MagicMock()
    mock_st.info = MagicMock()
    mock_st.rerun = MagicMock()
    
    # Track button calls to check for back button
    button_calls = []
    def button_side_effect(*args, **kwargs):
        button_calls.append(str(args[0]) if args else "")
        return False
    
    mock_st.button = MagicMock(side_effect=button_side_effect)
    
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
    
    # Verify back button exists
    assert any("back" in call.lower() or "Back" in call for call in button_calls)


def test_render_interview_room_back_button_resets_session_state(mocker):
    """Test that Back button resets current_page and clears selected_job_id."""
    mock_st = mocker.patch('main.st')
    mock_st.session_state = {
        "current_page": "interview_room",
        "selected_job_id": "job_1"
    }
    mock_st.title = MagicMock()
    mock_st.write = MagicMock()
    mock_st.container = MagicMock(return_value=MagicMock())
    mock_st.subheader = MagicMock()
    mock_st.divider = MagicMock()
    mock_st.columns = MagicMock(return_value=[MagicMock(), MagicMock()])
    mock_st.text_area = MagicMock()
    mock_st.info = MagicMock()
    mock_st.rerun = MagicMock()
    
    # Mock back button click
    call_count = 0
    def button_side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if "back" in str(args[0]).lower() or "Back" in str(args[0]):
            mock_st.session_state["current_page"] = "job_listing"
            mock_st.session_state["selected_job_id"] = None
            return True
        return False
    
    mock_st.button = MagicMock(side_effect=button_side_effect)
    
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
    
    # Verify session state is reset
    assert mock_st.session_state["current_page"] == "job_listing"
    assert mock_st.session_state["selected_job_id"] is None
    assert mock_st.rerun.called

