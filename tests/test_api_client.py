"""Tests for frontend API client."""
import pytest
from unittest.mock import patch, MagicMock
from api_client import start_interview, submit_answer, end_interview, get_session, get_evaluation, APIError


@patch("api_client.httpx.post")
def test_start_interview_success(mock_post):
    """Test starting an interview successfully."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "session_id": "test-session-123",
        "question": "Why are you interested?",
        "question_number": 1
    }
    mock_post.return_value = mock_response
    
    result = start_interview("job_1")
    
    assert result["session_id"] == "test-session-123"
    assert result["question"] == "Why are you interested?"
    assert result["question_number"] == 1
    mock_post.assert_called_once()


@patch("api_client.httpx.post")
def test_start_interview_network_error(mock_post):
    """Test handling network error."""
    mock_post.side_effect = Exception("Network error")
    
    with pytest.raises(APIError, match="Network error"):
        start_interview("job_1")


@patch("api_client.httpx.post")
def test_start_interview_api_error(mock_post):
    """Test handling API error response."""
    import httpx
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"detail": "Job not found"}
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Bad Request",
        request=MagicMock(),
        response=mock_response
    )
    mock_post.return_value = mock_response
    
    with pytest.raises(APIError, match="Job not found"):
        start_interview("invalid_job")


@patch("api_client.httpx.post")
def test_submit_answer_success(mock_post):
    """Test submitting an answer successfully."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "question": "Next question?",
        "question_number": 2,
        "interview_complete": False
    }
    mock_post.return_value = mock_response
    
    result = submit_answer("session-123", "My answer")
    
    assert result["question"] == "Next question?"
    assert result["question_number"] == 2
    assert result["interview_complete"] is False
    mock_post.assert_called_once()


@patch("api_client.httpx.post")
def test_submit_answer_complete(mock_post):
    """Test submitting answer when interview is complete."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "question": None,
        "question_number": 6,
        "interview_complete": True
    }
    mock_post.return_value = mock_response
    
    result = submit_answer("session-123", "Final answer")
    
    assert result["question"] is None
    assert result["interview_complete"] is True


@patch("api_client.httpx.post")
def test_submit_answer_error(mock_post):
    """Test handling error when submitting answer."""
    import httpx
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"detail": "Session not found"}
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Bad Request",
        request=MagicMock(),
        response=mock_response
    )
    mock_post.return_value = mock_response
    
    with pytest.raises(APIError, match="Session not found"):
        submit_answer("invalid-session", "Answer")


@patch("api_client.httpx.post")
def test_end_interview_success(mock_post):
    """Test ending an interview successfully."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "session_id": "session-123",
        "message": "Interview ended successfully"
    }
    mock_post.return_value = mock_response
    
    result = end_interview("session-123")
    
    assert result["session_id"] == "session-123"
    assert "message" in result
    mock_post.assert_called_once()


@patch("api_client.httpx.post")
def test_end_interview_error(mock_post):
    """Test handling error when ending interview."""
    import httpx
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"detail": "Session not found"}
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Bad Request",
        request=MagicMock(),
        response=mock_response
    )
    mock_post.return_value = mock_response
    
    with pytest.raises(APIError, match="Session not found"):
        end_interview("invalid-session")


@patch("api_client.httpx.get")
def test_get_session_success(mock_get):
    """Test getting a session successfully."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "session_id": "session-123",
        "job_id": "job_1",
        "job_title": "Software Engineer",
        "job_department": "Engineering",
        "conversation_history": [],
        "started_at": "2024-01-01T00:00:00Z",
        "ended_at": "2024-01-01T01:00:00Z"
    }
    mock_get.return_value = mock_response
    
    result = get_session("session-123")
    
    assert result["session_id"] == "session-123"
    assert result["job_id"] == "job_1"
    assert result["job_title"] == "Software Engineer"
    mock_get.assert_called_once()


@patch("api_client.httpx.get")
def test_get_session_error(mock_get):
    """Test handling error when getting session."""
    import httpx
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.return_value = {"detail": "Session not found"}
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Not Found",
        request=MagicMock(),
        response=mock_response
    )
    mock_get.return_value = mock_response
    
    with pytest.raises(APIError, match="Session not found"):
        get_session("nonexistent-session")


@patch("api_client.httpx.get")
def test_get_evaluation_success(mock_get):
    """Test getting an evaluation successfully."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "strengths": ["Strong technical skills", "Good communication"],
        "concerns": ["Limited experience"],
        "overall_score": 85.0
    }
    mock_get.return_value = mock_response
    
    result = get_evaluation("session-123")
    
    assert "strengths" in result
    assert "concerns" in result
    assert "overall_score" in result
    assert result["overall_score"] == 85.0
    assert len(result["strengths"]) == 2
    mock_get.assert_called_once()


@patch("api_client.httpx.get")
def test_get_evaluation_error(mock_get):
    """Test handling error when getting evaluation."""
    import httpx
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"detail": "Session not complete"}
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Bad Request",
        request=MagicMock(),
        response=mock_response
    )
    mock_get.return_value = mock_response
    
    with pytest.raises(APIError, match="Session not complete"):
        get_evaluation("session-123")


# --- Transcription retry tests ---

@patch("api_client.time.sleep")
@patch("api_client.httpx.post")
def test_transcribe_audio_retries_on_503(mock_post, mock_sleep):
    """Test that transcribe_audio retries on 503 status code."""
    import httpx
    from api_client import transcribe_audio
    
    # First call: 503 error
    mock_response_503 = MagicMock()
    mock_response_503.status_code = 503
    mock_response_503.json.return_value = {"detail": "Service busy"}
    mock_response_503.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Service Unavailable",
        request=MagicMock(),
        response=mock_response_503
    )
    
    # Second call: success
    mock_response_ok = MagicMock()
    mock_response_ok.status_code = 200
    mock_response_ok.json.return_value = {"text": "Transcribed text"}
    mock_response_ok.raise_for_status = MagicMock()  # No exception
    
    mock_post.side_effect = [mock_response_503, mock_response_ok]
    
    result = transcribe_audio(b"audio data", "test.wav")
    
    assert result == "Transcribed text"
    assert mock_post.call_count == 2
    mock_sleep.assert_called_once()  # Should have slept once between retries


@patch("api_client.time.sleep")
@patch("api_client.httpx.post")
def test_transcribe_audio_exhausts_retries_on_persistent_503(mock_post, mock_sleep):
    """Test that transcribe_audio raises error after exhausting retries."""
    import httpx
    from api_client import transcribe_audio
    
    # All calls return 503
    mock_response_503 = MagicMock()
    mock_response_503.status_code = 503
    mock_response_503.json.return_value = {"detail": "Service busy"}
    mock_response_503.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Service Unavailable",
        request=MagicMock(),
        response=mock_response_503
    )
    
    mock_post.return_value = mock_response_503
    
    with pytest.raises(APIError, match="Service busy"):
        transcribe_audio(b"audio data", "test.wav")
    
    # Should have tried 4 times (initial + 3 retries)
    assert mock_post.call_count == 4


@patch("api_client.time.sleep")
@patch("api_client.httpx.post")
def test_transcribe_audio_no_retry_on_400(mock_post, mock_sleep):
    """Test that transcribe_audio does NOT retry on 400 errors."""
    import httpx
    from api_client import transcribe_audio
    
    mock_response_400 = MagicMock()
    mock_response_400.status_code = 400
    mock_response_400.json.return_value = {"detail": "Invalid format"}
    mock_response_400.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Bad Request",
        request=MagicMock(),
        response=mock_response_400
    )
    
    mock_post.return_value = mock_response_400
    
    with pytest.raises(APIError, match="Invalid format"):
        transcribe_audio(b"audio data", "test.wav")
    
    # Should have tried only once - no retry on 400
    assert mock_post.call_count == 1
    mock_sleep.assert_not_called()

