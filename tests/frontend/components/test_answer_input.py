"""Tests for answer input component."""
import pytest
from unittest.mock import MagicMock
from models.job import Job


def test_render_answer_input_recording_state_idle(mocker):
    """Test that answer input displays idle state correctly."""
    mock_st = mocker.patch('frontend.components.answer_input.st')
    mock_st.subheader = MagicMock()
    mock_st.info = MagicMock()
    mock_st.form = MagicMock(return_value=MagicMock())
    mock_st.text_area = MagicMock()
    mock_st.file_uploader = MagicMock(return_value=None)
    
    # Mock audio recorder component
    mocker.patch('frontend.components.answer_input.render_audio_recorder')
    
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
    
    mock_st.subheader.assert_called_with("Your Answer")


def test_render_answer_input_shows_transcribed_text_readonly(mocker):
    """Test that transcribed text is displayed in read-only mode (normal mode)."""
    mock_st = mocker.patch('frontend.components.answer_input.st')
    mock_st.subheader = MagicMock()
    mock_st.info = MagicMock()
    mock_st.text_area = MagicMock()
    mock_st.file_uploader = MagicMock(return_value=None)
    mock_st.button = MagicMock(return_value=False)
    
    # Mock audio recorder component
    mocker.patch('frontend.components.answer_input.render_audio_recorder')
    
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
        "transcribed_text": "This is transcribed text",
        "debug_mode": False,
    }
    
    from frontend.components.answer_input import render_answer_input
    render_answer_input(job, interview_state)
    
    # Should display transcribed text (read-only)
    assert mock_st.text_area.called or mock_st.info.called


def test_render_answer_input_shows_transcribed_text_editable_debug(mocker):
    """Test that transcribed text is editable in debug mode."""
    mock_st = mocker.patch('frontend.components.answer_input.st')
    mock_st.subheader = MagicMock()
    mock_st.info = MagicMock()
    mock_st.text_area = MagicMock()
    mock_st.file_uploader = MagicMock(return_value=None)
    mock_st.button = MagicMock(return_value=False)
    
    # Mock audio recorder component
    mocker.patch('frontend.components.answer_input.render_audio_recorder')
    
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
        "transcribed_text": "This is transcribed text",
        "debug_mode": True,
    }
    
    from frontend.components.answer_input import render_answer_input
    render_answer_input(job, interview_state)
    
    # Should show editable text area in debug mode
    assert mock_st.text_area.called


def test_render_answer_input_renders_audio_recorder(mocker):
    """Test that audio recorder component is rendered."""
    mock_st = mocker.patch('frontend.components.answer_input.st')
    mock_st.subheader = MagicMock()
    mock_st.info = MagicMock()
    mock_st.file_uploader = MagicMock(return_value=None)
    
    mock_render_audio_recorder = mocker.patch('frontend.components.answer_input.render_audio_recorder')
    
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
        "spacebar_enabled": True,
    }
    
    from frontend.components.answer_input import render_answer_input
    render_answer_input(job, interview_state)
    
    # Should call audio recorder component
    mock_render_audio_recorder.assert_called()


def test_render_answer_input_renders_file_uploader(mocker):
    """Test that audio file uploader is rendered."""
    mock_st = mocker.patch('frontend.components.answer_input.st')
    mock_st.subheader = MagicMock()
    mock_st.info = MagicMock()
    mock_st.file_uploader = MagicMock(return_value=None)
    
    # Mock audio recorder component
    mocker.patch('frontend.components.answer_input.render_audio_recorder')
    
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
    
    # Should call file uploader
    assert mock_st.file_uploader.called


def test_render_answer_input_shows_debug_submit_button(mocker):
    """Test that debug mode submit button appears when transcribed_text exists."""
    mock_st = mocker.patch('frontend.components.answer_input.st')
    mock_st.subheader = MagicMock()
    mock_st.info = MagicMock()
    mock_st.text_area = MagicMock(return_value="")
    mock_st.file_uploader = MagicMock(return_value=None)
    mock_st.button = MagicMock(return_value=False)
    
    # Mock audio recorder component
    mocker.patch('frontend.components.answer_input.render_audio_recorder')
    
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
        "transcribed_text": "Some text",
        "debug_mode": True,
    }
    
    from frontend.components.answer_input import render_answer_input
    render_answer_input(job, interview_state)
    
    # Should show submit button in debug mode when transcribed_text exists
    button_calls = [str(call) for call in mock_st.button.call_args_list]
    assert any("submit" in str(call).lower() for call in mock_st.button.call_args_list)


def test_render_answer_input_renders_fallback_text_input(mocker):
    """Test that fallback text input form is rendered."""
    mock_st = mocker.patch('frontend.components.answer_input.st')
    mock_st.subheader = MagicMock()
    mock_st.info = MagicMock()
    mock_st.form = MagicMock(return_value=MagicMock())
    mock_st.text_area = MagicMock()
    mock_st.file_uploader = MagicMock(return_value=None)
    
    # Mock audio recorder component
    mocker.patch('frontend.components.answer_input.render_audio_recorder')
    
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
    
    # Should render form with text input
    assert mock_st.form.called

