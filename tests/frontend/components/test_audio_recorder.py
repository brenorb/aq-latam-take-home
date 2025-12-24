"""Tests for audio recorder component."""
from unittest.mock import MagicMock

import pytest


def test_render_audio_recorder_calls_audio_recorder_component(mocker):
    """Test that render_audio_recorder uses the audio_recorder_streamlit component."""
    mock_st = mocker.patch('frontend.components.audio_recorder.st')
    mock_audio_recorder = mocker.patch(
        'frontend.components.audio_recorder.audio_recorder',
        return_value=None  # No audio recorded yet
    )
    
    interview_state = {
        "recording_state": "idle",
        "transcribed_text": "",
        "session_id": "test-session",
    }
    
    from frontend.components.audio_recorder import render_audio_recorder
    render_audio_recorder("job_1", interview_state)
    
    # Should call the audio_recorder component
    assert mock_audio_recorder.called


def test_render_audio_recorder_processes_audio_when_returned(mocker):
    """Test that audio bytes are processed when recorder returns data."""
    mock_st = mocker.patch('frontend.components.audio_recorder.st')
    mock_st.session_state = {}
    
    # Simulate audio recorder returning bytes
    fake_audio_bytes = b"fake wav audio data"
    mock_audio_recorder = mocker.patch(
        'frontend.components.audio_recorder.audio_recorder',
        return_value=fake_audio_bytes
    )
    
    mock_process_audio = mocker.patch(
        'frontend.components.audio_recorder.process_audio_from_bytes'
    )
    
    interview_state = {
        "recording_state": "idle",
        "transcribed_text": "",
        "session_id": "test-session",
    }
    
    from frontend.components.audio_recorder import render_audio_recorder
    render_audio_recorder("job_1", interview_state)
    
    # Should call process_audio_from_bytes with the audio data
    mock_process_audio.assert_called_once_with(fake_audio_bytes, "job_1", interview_state)


def test_render_audio_recorder_does_not_process_when_no_audio(mocker):
    """Test that nothing is processed when recorder returns None."""
    mock_st = mocker.patch('frontend.components.audio_recorder.st')
    mock_st.session_state = {}
    
    # Simulate no audio recorded
    mock_audio_recorder = mocker.patch(
        'frontend.components.audio_recorder.audio_recorder',
        return_value=None
    )
    
    mock_process_audio = mocker.patch(
        'frontend.components.audio_recorder.process_audio_from_bytes'
    )
    
    interview_state = {
        "recording_state": "idle",
        "transcribed_text": "",
        "session_id": "test-session",
    }
    
    from frontend.components.audio_recorder import render_audio_recorder
    render_audio_recorder("job_1", interview_state)
    
    # Should NOT call process_audio_from_bytes
    assert not mock_process_audio.called


def test_render_audio_recorder_avoids_reprocessing_same_audio(mocker):
    """Test that same audio bytes are not processed multiple times."""
    mock_st = mocker.patch('frontend.components.audio_recorder.st')
    
    fake_audio_bytes = b"fake wav audio data"
    # Simulate audio already processed (stored in session state)
    mock_st.session_state = {
        "last_audio_job_1": fake_audio_bytes
    }
    
    mock_audio_recorder = mocker.patch(
        'frontend.components.audio_recorder.audio_recorder',
        return_value=fake_audio_bytes  # Same audio returned again
    )
    
    mock_process_audio = mocker.patch(
        'frontend.components.audio_recorder.process_audio_from_bytes'
    )
    
    interview_state = {
        "recording_state": "idle",
        "transcribed_text": "",
        "session_id": "test-session",
    }
    
    from frontend.components.audio_recorder import render_audio_recorder
    render_audio_recorder("job_1", interview_state)
    
    # Should NOT reprocess the same audio
    assert not mock_process_audio.called


def test_render_audio_recorder_processes_new_audio_after_previous(mocker):
    """Test that new audio bytes are processed even after previous audio."""
    mock_st = mocker.patch('frontend.components.audio_recorder.st')
    
    old_audio = b"old audio data"
    new_audio = b"new audio data"
    # Simulate previous audio stored
    mock_st.session_state = {
        "last_audio_job_1": old_audio
    }
    
    mock_audio_recorder = mocker.patch(
        'frontend.components.audio_recorder.audio_recorder',
        return_value=new_audio  # New audio returned
    )
    
    mock_process_audio = mocker.patch(
        'frontend.components.audio_recorder.process_audio_from_bytes'
    )
    
    interview_state = {
        "recording_state": "idle",
        "transcribed_text": "",
        "session_id": "test-session",
    }
    
    from frontend.components.audio_recorder import render_audio_recorder
    render_audio_recorder("job_1", interview_state)
    
    # Should process the NEW audio
    mock_process_audio.assert_called_once_with(new_audio, "job_1", interview_state)


def test_render_audio_recorder_updates_session_state_after_processing(mocker):
    """Test that session state is updated after processing audio."""
    mock_st = mocker.patch('frontend.components.audio_recorder.st')
    mock_st.session_state = {}
    
    fake_audio_bytes = b"fake wav audio data"
    mock_audio_recorder = mocker.patch(
        'frontend.components.audio_recorder.audio_recorder',
        return_value=fake_audio_bytes
    )
    
    mock_process_audio = mocker.patch(
        'frontend.components.audio_recorder.process_audio_from_bytes'
    )
    
    interview_state = {
        "recording_state": "idle",
        "transcribed_text": "",
        "session_id": "test-session",
    }
    
    from frontend.components.audio_recorder import render_audio_recorder
    render_audio_recorder("job_1", interview_state)
    
    # Session state should be updated to track processed audio
    assert mock_st.session_state.get("last_audio_job_1") == fake_audio_bytes


def test_render_audio_recorder_handles_empty_bytes(mocker):
    """Test that empty bytes are not processed."""
    mock_st = mocker.patch('frontend.components.audio_recorder.st')
    mock_st.session_state = {}
    
    # Empty bytes (technically truthy but shouldn't be processed)
    empty_audio = b""
    mock_audio_recorder = mocker.patch(
        'frontend.components.audio_recorder.audio_recorder',
        return_value=empty_audio
    )
    
    mock_process_audio = mocker.patch(
        'frontend.components.audio_recorder.process_audio_from_bytes'
    )
    
    interview_state = {
        "recording_state": "idle",
        "transcribed_text": "",
        "session_id": "test-session",
    }
    
    from frontend.components.audio_recorder import render_audio_recorder
    render_audio_recorder("job_1", interview_state)
    
    # Should NOT process empty bytes
    assert not mock_process_audio.called
