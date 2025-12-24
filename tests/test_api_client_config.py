"""Tests for API client configuration (environment variables, timeout, error handling)."""
import os
import pytest
from unittest.mock import patch, MagicMock
import httpx
from api_client import start_interview, APIError, BASE_URL


def test_api_base_url_from_env():
    """Test that API base URL can be configured via environment variable."""
    with patch.dict(os.environ, {"API_BASE_URL": "https://api.example.com"}):
        import importlib
        import api_client
        importlib.reload(api_client)
        
        assert api_client.BASE_URL == "https://api.example.com"


def test_api_base_url_default():
    """Test that API base URL defaults to localhost:8000 when not set."""
    env_backup = os.environ.pop("API_BASE_URL", None)
    try:
        import importlib
        import api_client
        importlib.reload(api_client)
        
        assert api_client.BASE_URL == "http://localhost:8000"
    finally:
        if env_backup:
            os.environ["API_BASE_URL"] = env_backup


@patch("api_client.httpx.post")
def test_api_timeout_configuration(mock_post):
    """Test that API timeout can be configured via environment variable."""
    with patch.dict(os.environ, {"API_TIMEOUT": "30.0"}):
        import importlib
        import api_client
        importlib.reload(api_client)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"session_id": "test", "question": "test"}
        mock_post.return_value = mock_response
        
        start_interview("job_1")
        
        # Check that timeout was used in the call
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["timeout"] == 30.0


@patch("api_client.httpx.post")
def test_api_timeout_default(mock_post):
    """Test that API timeout defaults to 10.0 seconds when not set."""
    env_backup = os.environ.pop("API_TIMEOUT", None)
    try:
        import importlib
        import api_client
        importlib.reload(api_client)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"session_id": "test", "question": "test"}
        mock_post.return_value = mock_response
        
        start_interview("job_1")
        
        # Check that default timeout was used
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["timeout"] == 10.0
    finally:
        if env_backup:
            os.environ["API_TIMEOUT"] = env_backup


@patch("api_client.httpx.post")
def test_api_error_user_friendly_message(mock_post):
    """Test that API errors provide user-friendly messages."""
    import httpx
    
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.return_value = {"detail": "Internal server error"}
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Internal Server Error",
        request=MagicMock(),
        response=mock_response
    )
    mock_post.return_value = mock_response
    
    with pytest.raises(APIError) as exc_info:
        start_interview("job_1")
    
    # Error message should be user-friendly, not expose internal details
    error_msg = str(exc_info.value).lower()
    assert "api error" in error_msg or "internal server error" in error_msg
    assert "traceback" not in error_msg
    assert "file" not in error_msg


@patch("api_client.httpx.post")
def test_api_network_error_user_friendly(mock_post):
    """Test that network errors provide user-friendly messages."""
    mock_post.side_effect = httpx.ConnectError("Connection refused")
    
    with pytest.raises(APIError) as exc_info:
        start_interview("job_1")
    
    # Error message should be user-friendly
    error_msg = str(exc_info.value).lower()
    assert "network error" in error_msg or "connection" in error_msg
    assert "traceback" not in error_msg

