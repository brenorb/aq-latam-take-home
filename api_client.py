"""Frontend API client for communicating with FastAPI backend."""
import os
import time
import httpx


class APIError(Exception):
    """Exception raised for API errors."""
    pass


BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def start_interview(job_id: str) -> dict:
    """
    Start a new interview session.
    
    Args:
        job_id: ID of the job to interview for
        
    Returns:
        Dictionary with session_id, question, question_number, conversation_history
        
    Raises:
        APIError: If API call fails
    """
    try:
        response = httpx.post(
            f"{BASE_URL}/api/interviews/start",
            json={"job_id": job_id},
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        error_detail = "Unknown error"
        try:
            error_data = e.response.json()
            error_detail = error_data.get("detail", str(e))
        except Exception:
            error_detail = str(e)
        raise APIError(f"API error: {error_detail}") from e
    except Exception as e:
        raise APIError(f"Network error: {str(e)}") from e


def submit_answer(session_id: str, answer: str) -> dict:
    """
    Submit an answer and get the next question.
    
    Args:
        session_id: Session identifier
        answer: User's answer text
        
    Returns:
        Dictionary with question, question_number, interview_complete, conversation_history
        
    Raises:
        APIError: If API call fails
    """
    try:
        response = httpx.post(
            f"{BASE_URL}/api/interviews/{session_id}/answer",
            json={"answer": answer},
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        error_detail = "Unknown error"
        try:
            error_data = e.response.json()
            error_detail = error_data.get("detail", str(e))
        except Exception:
            error_detail = str(e)
        raise APIError(f"API error: {error_detail}") from e
    except Exception as e:
        raise APIError(f"Network error: {str(e)}") from e


def end_interview(session_id: str) -> dict:
    """
    End an interview session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Dictionary with session_id and message
        
    Raises:
        APIError: If API call fails
    """
    try:
        response = httpx.post(
            f"{BASE_URL}/api/interviews/{session_id}/end",
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        error_detail = "Unknown error"
        try:
            error_data = e.response.json()
            error_detail = error_data.get("detail", str(e))
        except Exception:
            error_detail = str(e)
        raise APIError(f"API error: {error_detail}") from e
    except Exception as e:
        raise APIError(f"Network error: {str(e)}") from e


def get_session(session_id: str) -> dict:
    """
    Retrieve a saved interview session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Dictionary with session data
        
    Raises:
        APIError: If API call fails
    """
    try:
        response = httpx.get(
            f"{BASE_URL}/api/interviews/{session_id}",
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        error_detail = "Unknown error"
        try:
            error_data = e.response.json()
            error_detail = error_data.get("detail", str(e))
        except Exception:
            error_detail = str(e)
        raise APIError(f"API error: {error_detail}") from e
    except Exception as e:
        raise APIError(f"Network error: {str(e)}") from e


def get_evaluation(session_id: str) -> dict:
    """
    Get evaluation for a completed interview session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Dictionary with strengths, concerns, and overall_score
        
    Raises:
        APIError: If API call fails
    """
    try:
        response = httpx.get(
            f"{BASE_URL}/api/interviews/{session_id}/evaluation",
            timeout=30.0  # Longer timeout for LLM evaluation
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        error_detail = "Unknown error"
        try:
            error_data = e.response.json()
            error_detail = error_data.get("detail", str(e))
        except Exception:
            error_detail = str(e)
        raise APIError(f"API error: {error_detail}") from e
    except Exception as e:
        raise APIError(f"Network error: {str(e)}") from e


def transcribe_audio(
    audio_data: bytes,
    filename: str = "audio.webm",
    max_retries: int = 3,
    base_delay: float = 1.0,
) -> str:
    """
    Transcribe audio file using backend transcription service.
    
    Includes retry logic with exponential backoff for 503 (service busy) errors.
    
    Args:
        audio_data: Audio file bytes
        filename: Name of the audio file
        max_retries: Maximum number of retry attempts (default: 3)
        base_delay: Base delay in seconds for exponential backoff (default: 1.0)
        
    Returns:
        Transcribed text string
        
    Raises:
        APIError: If API call fails after all retries
    """
    # Infer MIME type from filename extension
    ext = filename.split(".")[-1].lower() if "." in filename else "webm"
    mime_types = {
        "wav": "audio/wav",
        "webm": "audio/webm",
        "mp3": "audio/mpeg",
        "m4a": "audio/mp4",
        "mp4": "audio/mp4",
        "mpeg": "audio/mpeg",
        "mpga": "audio/mpeg",
    }
    mime_type = mime_types.get(ext, "audio/webm")
    
    last_error = None
    
    for attempt in range(max_retries + 1):
        try:
            files = {"file": (filename, audio_data, mime_type)}
            response = httpx.post(
                f"{BASE_URL}/api/transcribe",
                files=files,
                timeout=30.0  # Longer timeout for transcription
            )
            response.raise_for_status()
            result = response.json()
            return result.get("text", "")
        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_data = e.response.json()
                error_detail = error_data.get("detail", str(e))
            except Exception:
                error_detail = str(e)
            
            # Retry on 503 (service busy)
            if e.response.status_code == 503 and attempt < max_retries:
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
                last_error = APIError(f"API error: {error_detail}")
                continue
            
            raise APIError(f"API error: {error_detail}") from e
        except Exception as e:
            raise APIError(f"Network error: {str(e)}") from e
    
    # Should not reach here, but just in case
    if last_error:
        raise last_error
    raise APIError("Transcription failed after retries")
