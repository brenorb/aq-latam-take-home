"""Frontend API client for communicating with FastAPI backend."""
import os
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

