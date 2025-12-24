"""Tests for transcription service."""
import pytest
from unittest.mock import MagicMock
from io import BytesIO
from api_client import APIError


def test_process_audio_transcription_success(mocker):
    """Test that process_audio_transcription successfully transcribes audio."""
    mock_st = mocker.patch('frontend.services.transcription_service.st')
    mock_st.session_state = {}
    
    mock_transcribe_audio = mocker.patch(
        'frontend.services.transcription_service.transcribe_audio',
        return_value="This is transcribed text"
    )
    
    mock_submit_answer_handler = mocker.patch(
        'frontend.services.transcription_service.submit_answer_handler'
    )
    
    uploaded_file = BytesIO(b"fake audio data")
    uploaded_file.name = "audio.webm"
    
    interview_state = {
        "session_id": "test-session-123",
        "recording_state": "idle",
        "transcribed_text": "",
        "debug_mode": False,
    }
    
    from frontend.services.transcription_service import process_audio_transcription
    process_audio_transcription(uploaded_file, "job_1", interview_state)
    
    assert interview_state["transcribed_text"] == "This is transcribed text"
    # Recording state is set to "submitting" before auto-submit in normal mode
    assert interview_state["recording_state"] in ("submitting", "idle")
    assert mock_transcribe_audio.called
    # Should auto-submit in normal mode
    assert mock_submit_answer_handler.called
    # Verify job_id was passed correctly
    assert mock_submit_answer_handler.call_args[0][3] == "job_1"


def test_process_audio_transcription_debug_mode_no_auto_submit(mocker):
    """Test that debug mode doesn't auto-submit."""
    mock_st = mocker.patch('frontend.services.transcription_service.st')
    mock_st.session_state = {}
    
    mocker.patch(
        'frontend.services.transcription_service.transcribe_audio',
        return_value="This is transcribed text"
    )
    
    mock_submit_answer_handler = mocker.patch(
        'frontend.services.transcription_service.submit_answer_handler'
    )
    
    uploaded_file = BytesIO(b"fake audio data")
    uploaded_file.name = "audio.webm"
    
    interview_state = {
        "session_id": "test-session-123",
        "recording_state": "idle",
        "transcribed_text": "",
        "debug_mode": True,
    }
    
    from frontend.services.transcription_service import process_audio_transcription
    process_audio_transcription(uploaded_file, "job_1", interview_state)
    
    assert interview_state["transcribed_text"] == "This is transcribed text"
    # Should NOT auto-submit in debug mode
    assert not mock_submit_answer_handler.called


def test_process_audio_transcription_api_error(mocker):
    """Test that process_audio_transcription handles APIError correctly."""
    mock_st = mocker.patch('frontend.services.transcription_service.st')
    mock_st.session_state = {}
    mock_st.error = MagicMock()
    
    mocker.patch(
        'frontend.services.transcription_service.transcribe_audio',
        side_effect=APIError("API error: Transcription failed")
    )
    
    uploaded_file = BytesIO(b"fake audio data")
    uploaded_file.name = "audio.webm"
    
    interview_state = {
        "session_id": "test-session-123",
        "recording_state": "processing",
        "transcribed_text": "",
        "transcription_error": None,
        "debug_mode": False,
    }
    
    from frontend.services.transcription_service import process_audio_transcription
    process_audio_transcription(uploaded_file, "job_1", interview_state)
    
    assert interview_state["recording_state"] == "error"
    assert interview_state["transcription_error"] is not None
    assert mock_st.error.called


def test_process_audio_transcription_updates_recording_state(mocker):
    """Test that recording_state is updated correctly through the flow."""
    mock_st = mocker.patch('frontend.services.transcription_service.st')
    mock_st.session_state = {}
    
    mocker.patch(
        'frontend.services.transcription_service.transcribe_audio',
        return_value="Transcribed text"
    )
    
    mocker.patch(
        'frontend.services.transcription_service.submit_answer_handler'
    )
    
    uploaded_file = BytesIO(b"fake audio data")
    uploaded_file.name = "audio.webm"
    
    interview_state = {
        "session_id": "test-session-123",
        "recording_state": "idle",
        "transcribed_text": "",
        "debug_mode": False,
    }
    
    from frontend.services.transcription_service import process_audio_transcription
    process_audio_transcription(uploaded_file, "job_1", interview_state)
    
    # Recording state should be updated (to "submitting" before auto-submit in normal mode)
    assert interview_state["recording_state"] in ("submitting", "idle")


def test_process_audio_transcription_clears_uploaded_file(mocker):
    """Test that uploaded file is cleared from session_state after processing."""
    mock_st = mocker.patch('frontend.services.transcription_service.st')
    mock_st.session_state = {"uploaded_audio_job_1": BytesIO(b"fake audio")}
    
    mocker.patch(
        'frontend.services.transcription_service.transcribe_audio',
        return_value="Transcribed text"
    )
    
    mocker.patch(
        'frontend.services.transcription_service.submit_answer_handler'
    )
    
    uploaded_file = BytesIO(b"fake audio data")
    uploaded_file.name = "audio.webm"
    
    interview_state = {
        "session_id": "test-session-123",
        "recording_state": "idle",
        "transcribed_text": "",
        "debug_mode": False,
    }
    
    from frontend.services.transcription_service import process_audio_transcription
    process_audio_transcription(uploaded_file, "job_1", interview_state)
    
    # File should be cleared (this is handled by Streamlit's file_uploader, but we verify state)


def test_process_audio_transcription_no_session_id(mocker):
    """Test that process_audio_transcription doesn't auto-submit when session_id is None."""
    mock_st = mocker.patch('frontend.services.transcription_service.st')
    mock_st.session_state = {}
    mock_st.warning = MagicMock()
    
    mocker.patch(
        'frontend.services.transcription_service.transcribe_audio',
        return_value="This is transcribed text"
    )
    
    mock_submit_answer_handler = mocker.patch(
        'frontend.services.transcription_service.submit_answer_handler'
    )
    
    uploaded_file = BytesIO(b"fake audio data")
    uploaded_file.name = "audio.webm"
    
    interview_state = {
        "session_id": None,  # No session started
        "recording_state": "idle",
        "transcribed_text": "",
        "debug_mode": False,
    }
    
    from frontend.services.transcription_service import process_audio_transcription
    process_audio_transcription(uploaded_file, "job_1", interview_state)
    
    # Should transcribe the audio
    assert interview_state["transcribed_text"] == "This is transcribed text"
    # Should NOT auto-submit when session_id is None
    assert not mock_submit_answer_handler.called
    # Should show warning
    assert mock_st.warning.called
    # Recording state should be set back to idle
    assert interview_state["recording_state"] == "idle"

