"""Tests for transcription service."""
import pytest
from unittest.mock import MagicMock
from api_client import APIError


def test_process_audio_from_bytes_success(mocker):
    """Test that process_audio_from_bytes successfully transcribes raw audio bytes."""
    mock_st = mocker.patch('frontend.services.transcription_service.st')
    mock_st.session_state = {}
    
    mock_transcribe_audio = mocker.patch(
        'frontend.services.transcription_service.transcribe_audio',
        return_value="Hello, this is my answer"
    )
    
    mock_submit_answer_handler = mocker.patch(
        'frontend.services.transcription_service.submit_answer_handler'
    )
    
    audio_bytes = b"fake wav audio data"
    
    interview_state = {
        "session_id": "test-session-456",
        "recording_state": "idle",
        "transcribed_text": "",
        "debug_mode": False,
    }
    
    from frontend.services.transcription_service import process_audio_from_bytes
    process_audio_from_bytes(audio_bytes, "job_2", interview_state)
    
    # Should call transcribe_audio with the bytes directly
    mock_transcribe_audio.assert_called_once_with(audio_bytes, "recording.wav")
    # Should update transcribed_text
    assert interview_state["transcribed_text"] == "Hello, this is my answer"
    # Should auto-submit in normal mode
    assert mock_submit_answer_handler.called
    assert mock_submit_answer_handler.call_args[0][1] == "Hello, this is my answer"
    assert mock_submit_answer_handler.call_args[0][3] == "job_2"


def test_process_audio_from_bytes_debug_mode_no_auto_submit(mocker):
    """Test that debug mode doesn't auto-submit with bytes."""
    mock_st = mocker.patch('frontend.services.transcription_service.st')
    mock_st.session_state = {}
    
    mocker.patch(
        'frontend.services.transcription_service.transcribe_audio',
        return_value="Debug transcription"
    )
    
    mock_submit_answer_handler = mocker.patch(
        'frontend.services.transcription_service.submit_answer_handler'
    )
    
    audio_bytes = b"fake wav audio data"
    
    interview_state = {
        "session_id": "test-session-456",
        "recording_state": "idle",
        "transcribed_text": "",
        "debug_mode": True,
    }
    
    from frontend.services.transcription_service import process_audio_from_bytes
    process_audio_from_bytes(audio_bytes, "job_2", interview_state)
    
    assert interview_state["transcribed_text"] == "Debug transcription"
    # Should NOT auto-submit in debug mode
    assert not mock_submit_answer_handler.called
    # Recording state should be idle (not submitting)
    assert interview_state["recording_state"] == "idle"


def test_process_audio_from_bytes_no_session_id(mocker):
    """Test that process_audio_from_bytes doesn't auto-submit when session_id is None."""
    mock_st = mocker.patch('frontend.services.transcription_service.st')
    mock_st.session_state = {}
    mock_st.warning = MagicMock()
    
    mocker.patch(
        'frontend.services.transcription_service.transcribe_audio',
        return_value="Transcribed without session"
    )
    
    mock_submit_answer_handler = mocker.patch(
        'frontend.services.transcription_service.submit_answer_handler'
    )
    
    audio_bytes = b"fake wav audio data"
    
    interview_state = {
        "session_id": None,
        "recording_state": "idle",
        "transcribed_text": "",
        "debug_mode": False,
    }
    
    from frontend.services.transcription_service import process_audio_from_bytes
    process_audio_from_bytes(audio_bytes, "job_2", interview_state)
    
    assert interview_state["transcribed_text"] == "Transcribed without session"
    assert not mock_submit_answer_handler.called
    assert mock_st.warning.called
    assert interview_state["recording_state"] == "idle"


def test_process_audio_from_bytes_api_error(mocker):
    """Test that process_audio_from_bytes handles APIError correctly."""
    mock_st = mocker.patch('frontend.services.transcription_service.st')
    mock_st.session_state = {}
    mock_st.error = MagicMock()
    
    mocker.patch(
        'frontend.services.transcription_service.transcribe_audio',
        side_effect=APIError("Transcription service unavailable")
    )
    
    audio_bytes = b"fake wav audio data"
    
    interview_state = {
        "session_id": "test-session-456",
        "recording_state": "idle",
        "transcribed_text": "",
        "transcription_error": None,
        "debug_mode": False,
    }
    
    from frontend.services.transcription_service import process_audio_from_bytes
    process_audio_from_bytes(audio_bytes, "job_2", interview_state)
    
    assert interview_state["recording_state"] == "error"
    assert interview_state["transcription_error"] == "Transcription service unavailable"
    assert mock_st.error.called


def test_process_audio_from_bytes_generic_exception(mocker):
    """Test that process_audio_from_bytes handles generic exceptions."""
    mock_st = mocker.patch('frontend.services.transcription_service.st')
    mock_st.session_state = {}
    mock_st.error = MagicMock()
    
    mocker.patch(
        'frontend.services.transcription_service.transcribe_audio',
        side_effect=Exception("Unexpected error")
    )
    
    audio_bytes = b"fake wav audio data"
    
    interview_state = {
        "session_id": "test-session-456",
        "recording_state": "idle",
        "transcribed_text": "",
        "transcription_error": None,
        "debug_mode": False,
    }
    
    from frontend.services.transcription_service import process_audio_from_bytes
    process_audio_from_bytes(audio_bytes, "job_2", interview_state)
    
    assert interview_state["recording_state"] == "error"
    assert "Unexpected error" in interview_state["transcription_error"]
    assert mock_st.error.called


def test_process_audio_from_bytes_shows_retrying_state_on_503(mocker):
    """Test that process_audio_from_bytes shows retrying state on 503 errors."""
    mock_st = mocker.patch('frontend.services.transcription_service.st')
    mock_st.session_state = {}
    mock_st.info = MagicMock()
    
    mock_sleep = mocker.patch('frontend.services.transcription_service.time.sleep')
    
    call_count = 0
    def transcribe_side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            # First call: raise 503 error
            raise APIError("API error: Service busy (503)")
        # Second call: success
        return "Transcribed after retry"
    
    mocker.patch(
        'frontend.services.transcription_service.transcribe_audio',
        side_effect=transcribe_side_effect
    )
    
    mock_submit_answer_handler = mocker.patch(
        'frontend.services.transcription_service.submit_answer_handler'
    )
    
    audio_bytes = b"fake wav audio data"
    
    interview_state = {
        "session_id": "test-session-456",
        "recording_state": "idle",
        "transcribed_text": "",
        "transcription_error": None,
        "debug_mode": False,
        "retry_attempt": 0,
        "max_retries": 3,
    }
    
    from frontend.services.transcription_service import process_audio_from_bytes
    process_audio_from_bytes(audio_bytes, "job_2", interview_state)
    
    # Should have succeeded on second try
    assert interview_state["transcribed_text"] == "Transcribed after retry"
    assert interview_state["recording_state"] == "submitting"
    # Should have called sleep once for retry delay
    assert mock_sleep.called


def test_process_audio_from_bytes_exhausts_retries_on_persistent_503(mocker):
    """Test that process_audio_from_bytes fails after exhausting retries."""
    mock_st = mocker.patch('frontend.services.transcription_service.st')
    mock_st.session_state = {}
    mock_st.error = MagicMock()
    mock_st.info = MagicMock()
    
    mock_sleep = mocker.patch('frontend.services.transcription_service.time.sleep')
    
    # All calls fail with 503
    mocker.patch(
        'frontend.services.transcription_service.transcribe_audio',
        side_effect=APIError("API error: Service busy (503)")
    )
    
    audio_bytes = b"fake wav audio data"
    
    interview_state = {
        "session_id": "test-session-456",
        "recording_state": "idle",
        "transcribed_text": "",
        "transcription_error": None,
        "debug_mode": False,
        "retry_attempt": 0,
        "max_retries": 3,
    }
    
    from frontend.services.transcription_service import process_audio_from_bytes
    process_audio_from_bytes(audio_bytes, "job_2", interview_state)
    
    # Should have failed after retries
    assert interview_state["recording_state"] == "error"
    assert interview_state["transcription_error"] is not None
    assert mock_st.error.called
    # Should have called sleep 3 times (for 3 retries)
    assert mock_sleep.call_count == 3
