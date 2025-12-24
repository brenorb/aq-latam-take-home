"""Tests for transcription endpoint."""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from io import BytesIO
from backend.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def mock_transcription_service():
    """Mock TranscriptionService for all transcription endpoint tests."""
    with patch("backend.api.routes.transcription_service") as mock_service_instance:
        mock_service_instance.transcribe.return_value = "This is transcribed text"
        yield mock_service_instance


def test_transcribe_endpoint_success(client, mock_transcription_service):
    """Test successful transcription."""
    audio_data = b"fake audio data"
    files = {"file": ("test.webm", BytesIO(audio_data), "audio/webm")}
    
    response = client.post("/api/transcribe", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert "text" in data
    assert data["text"] == "This is transcribed text"
    assert mock_transcription_service.transcribe.called


def test_transcribe_endpoint_invalid_format(client, mock_transcription_service):
    """Test transcription with invalid audio format."""
    mock_transcription_service.transcribe.side_effect = ValueError(
        "Unsupported audio format: unsupported. Supported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm"
    )
    
    audio_data = b"fake audio data"
    files = {"file": ("test.unsupported", BytesIO(audio_data), "audio/unsupported")}
    
    response = client.post("/api/transcribe", files=files)
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Unsupported audio format" in data["detail"]


def test_transcribe_endpoint_file_too_large(client, mock_transcription_service):
    """Test transcription with file that's too large."""
    mock_transcription_service.transcribe.side_effect = ValueError(
        "File size (30.00MB) exceeds maximum allowed size (25MB)"
    )
    
    audio_data = b"fake audio data"
    files = {"file": ("large.webm", BytesIO(audio_data), "audio/webm")}
    
    response = client.post("/api/transcribe", files=files)
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "exceeds maximum" in data["detail"]


def test_transcribe_endpoint_rate_limit_error_returns_503(client, mock_transcription_service):
    """Test transcription with rate limit error returns 503 with Retry-After header."""
    mock_transcription_service.transcribe.side_effect = Exception(
        "Transcription service is busy. Please wait a moment and try again."
    )
    
    audio_data = b"fake audio data"
    files = {"file": ("test.webm", BytesIO(audio_data), "audio/webm")}
    
    response = client.post("/api/transcribe", files=files)
    
    assert response.status_code == 503
    assert "retry-after" in response.headers
    assert response.headers["retry-after"] == "2"
    data = response.json()
    assert "detail" in data
    assert "busy" in data["detail"].lower()


def test_transcribe_endpoint_missing_file(client):
    """Test transcription endpoint without file."""
    response = client.post("/api/transcribe")
    
    assert response.status_code == 422  # Validation error


def test_transcribe_endpoint_supported_formats(client, mock_transcription_service):
    """Test that all supported formats work."""
    supported_formats = ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"]
    audio_data = b"fake audio data"
    
    for fmt in supported_formats:
        files = {"file": (f"test.{fmt}", BytesIO(audio_data), f"audio/{fmt}")}
        response = client.post("/api/transcribe", files=files)
        
        assert response.status_code == 200, f"Format {fmt} should be supported"
        data = response.json()
        assert "text" in data


def test_transcribe_endpoint_api_error(client, mock_transcription_service):
    """Test transcription with API error."""
    mock_transcription_service.transcribe.side_effect = Exception(
        "Transcription service error: API error occurred"
    )
    
    audio_data = b"fake audio data"
    files = {"file": ("test.webm", BytesIO(audio_data), "audio/webm")}
    
    response = client.post("/api/transcribe", files=files)
    
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data


def test_transcribe_endpoint_handles_bytes_correctly(client, mock_transcription_service):
    """Test that audio bytes are passed correctly to service."""
    audio_data = b"fake audio data for transcription"
    files = {"file": ("test.webm", BytesIO(audio_data), "audio/webm")}
    
    response = client.post("/api/transcribe", files=files)
    
    assert response.status_code == 200
    # Verify that transcribe was called with file-like object
    assert mock_transcription_service.transcribe.called
    call_args = mock_transcription_service.transcribe.call_args
    assert call_args is not None
    # Check that filename was passed
    assert len(call_args[0]) >= 1 or "filename" in call_args[1]

