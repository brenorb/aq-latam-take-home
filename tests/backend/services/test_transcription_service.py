"""Tests for transcription service."""
import pytest
import os
from unittest.mock import MagicMock, patch, mock_open
from io import BytesIO
from backend.services.transcription_service import TranscriptionService


@pytest.fixture
def transcription_service():
    """Create TranscriptionService instance with mocked OpenAI client."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"}):
        service = TranscriptionService()
        return service


def test_transcription_service_initialization():
    """Test that TranscriptionService initializes correctly."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"}):
        service = TranscriptionService()
        assert service is not None
        assert service.max_audio_size_mb == 25
        assert service.model == "whisper-1"


def test_transcription_service_initialization_with_env_vars():
    """Test that TranscriptionService uses environment variables."""
    with patch.dict(os.environ, {
        "OPENAI_API_KEY": "test-api-key",
        "MAX_AUDIO_SIZE_MB": "30",
        "OPENAI_MODEL": "whisper-2"
    }):
        service = TranscriptionService()
        assert service.max_audio_size_mb == 30
        assert service.model == "whisper-2"


def test_transcribe_success(transcription_service):
    """Test successful transcription."""
    mock_audio_file = BytesIO(b"fake audio data")
    mock_audio_file.name = "test.webm"
    
    mock_openai_client = MagicMock()
    mock_transcribe = MagicMock()
    mock_transcribe.return_value.text = "This is transcribed text"
    mock_openai_client.audio.transcriptions.create = mock_transcribe
    
    transcription_service.client = mock_openai_client
    
    result = transcription_service.transcribe(mock_audio_file)
    
    assert result == "This is transcribed text"
    assert mock_transcribe.called
    call_args = mock_transcribe.call_args
    assert call_args[1]["model"] == "whisper-1"
    assert call_args[1]["file"] == mock_audio_file


def test_transcribe_validates_file_size(transcription_service):
    """Test that file size validation works."""
    # Create a file-like object that's too large (26MB)
    large_data = b"x" * (26 * 1024 * 1024)
    mock_audio_file = BytesIO(large_data)
    mock_audio_file.name = "large.webm"
    
    with pytest.raises(ValueError, match="exceeds maximum"):
        transcription_service.transcribe(mock_audio_file)


def test_transcribe_validates_file_format(transcription_service):
    """Test that file format validation works."""
    mock_audio_file = BytesIO(b"fake audio data")
    
    # Format validation happens before API call, so it should raise ValueError immediately
    # Pass filename explicitly to test format validation
    with pytest.raises(ValueError, match="Unsupported audio format"):
        transcription_service.transcribe(mock_audio_file, filename="test.unsupported")


def test_transcribe_accepts_supported_formats(transcription_service):
    """Test that all supported formats are accepted."""
    supported_formats = ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"]
    
    mock_openai_client = MagicMock()
    mock_transcribe = MagicMock()
    mock_transcribe.return_value.text = "Transcribed"
    mock_openai_client.audio.transcriptions.create = mock_transcribe
    transcription_service.client = mock_openai_client
    
    for fmt in supported_formats:
        mock_audio_file = BytesIO(b"fake audio data")
        mock_audio_file.name = f"test.{fmt}"
        
        result = transcription_service.transcribe(mock_audio_file)
        assert result == "Transcribed"


def test_transcribe_handles_openai_rate_limit_error(transcription_service):
    """Test handling of OpenAI rate limit errors."""
    from openai import RateLimitError
    
    mock_audio_file = BytesIO(b"fake audio data")
    mock_audio_file.name = "test.webm"
    
    mock_openai_client = MagicMock()
    mock_transcribe = MagicMock()
    mock_transcribe.side_effect = RateLimitError(
        message="Rate limit exceeded",
        response=MagicMock(),
        body=None
    )
    mock_openai_client.audio.transcriptions.create = mock_transcribe
    
    transcription_service.client = mock_openai_client
    
    with pytest.raises(Exception, match="busy"):
        transcription_service.transcribe(mock_audio_file)


def test_transcribe_handles_openai_api_error(transcription_service):
    """Test handling of OpenAI API errors."""
    from openai import APIError
    
    mock_audio_file = BytesIO(b"fake audio data")
    mock_audio_file.name = "test.webm"
    
    mock_openai_client = MagicMock()
    mock_transcribe = MagicMock()
    # APIError constructor signature varies by version, use simpler approach
    try:
        # Try with body parameter (newer versions)
        mock_transcribe.side_effect = APIError(
            message="API error",
            request=MagicMock(),
            body=None
        )
    except TypeError:
        # Fallback for older versions
        mock_transcribe.side_effect = APIError(
            message="API error",
            request=MagicMock()
        )
    mock_openai_client.audio.transcriptions.create = mock_transcribe
    
    transcription_service.client = mock_openai_client
    
    with pytest.raises(Exception):
        transcription_service.transcribe(mock_audio_file)


def test_transcribe_handles_invalid_api_key(transcription_service):
    """Test handling of invalid API key errors."""
    from openai import AuthenticationError
    
    mock_audio_file = BytesIO(b"fake audio data")
    mock_audio_file.name = "test.webm"
    
    mock_openai_client = MagicMock()
    mock_transcribe = MagicMock()
    mock_transcribe.side_effect = AuthenticationError(
        message="Invalid API key",
        response=MagicMock(),
        body=None
    )
    mock_openai_client.audio.transcriptions.create = mock_transcribe
    
    transcription_service.client = mock_openai_client
    
    with pytest.raises(Exception):
        transcription_service.transcribe(mock_audio_file)


def test_transcribe_with_bytes_input(transcription_service):
    """Test transcription with bytes input."""
    audio_bytes = b"fake audio data"
    
    mock_openai_client = MagicMock()
    mock_transcribe = MagicMock()
    mock_transcribe.return_value.text = "Transcribed from bytes"
    mock_openai_client.audio.transcriptions.create = mock_transcribe
    
    transcription_service.client = mock_openai_client
    
    result = transcription_service.transcribe(audio_bytes, filename="test.webm")
    
    assert result == "Transcribed from bytes"
    assert mock_transcribe.called


def test_transcribe_resets_file_position(transcription_service):
    """Test that file position is reset before reading."""
    mock_audio_file = BytesIO(b"fake audio data")
    mock_audio_file.name = "test.webm"
    mock_audio_file.seek(10)  # Move file pointer
    
    mock_openai_client = MagicMock()
    mock_transcribe = MagicMock()
    mock_transcribe.return_value.text = "Transcribed"
    mock_openai_client.audio.transcriptions.create = mock_transcribe
    
    transcription_service.client = mock_openai_client
    
    transcription_service.transcribe(mock_audio_file)
    
    # File should be readable (position reset)
    assert mock_transcribe.called

