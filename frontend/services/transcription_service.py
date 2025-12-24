"""Transcription service for handling audio transcription."""
import time
import streamlit as st
from api_client import transcribe_audio, APIError
from frontend.services.interview_service import submit_answer_handler


# Retry configuration
MAX_RETRIES = 3
BASE_DELAY = 1.0


def _is_retryable_error(error: APIError) -> bool:
    """Check if an API error is retryable (503 or 'busy')."""
    error_msg = str(error).lower()
    return "503" in error_msg or "busy" in error_msg


def process_audio_from_bytes(audio_bytes: bytes, job_id: str, interview_state: dict) -> None:
    """
    Process audio transcription from raw bytes (e.g., from audio-recorder-streamlit).
    
    Includes retry logic with exponential backoff for transient errors (503).
    Shows retry status to the user via interview_state updates.
    
    Args:
        audio_bytes: Raw audio bytes (WAV format from recorder)
        job_id: ID of the job
        interview_state: Dictionary containing interview state (modified in place)
    """
    # Update state to processing
    interview_state["recording_state"] = "processing"
    interview_state["transcription_error"] = None
    interview_state["retry_attempt"] = 0
    
    max_retries = interview_state.get("max_retries", MAX_RETRIES)
    filename = "recording.wav"
    last_error = None
    
    for attempt in range(max_retries + 1):
        try:
            # Update retry state for UI feedback
            if attempt > 0:
                interview_state["recording_state"] = "retrying"
                interview_state["retry_attempt"] = attempt
                st.info(f"Retrying transcription (attempt {attempt}/{max_retries})...")
            
            # Call transcription API with raw bytes
            transcribed_text = transcribe_audio(audio_bytes, filename)
            
            # Success - update state with transcribed text
            interview_state["transcribed_text"] = transcribed_text
            interview_state["recording_state"] = "idle"
            interview_state["retry_attempt"] = 0
            
            # Auto-submit in normal mode (not debug mode)
            if not interview_state.get("debug_mode", False):
                session_id = interview_state.get("session_id")
                if session_id:
                    interview_state["recording_state"] = "submitting"
                    submit_answer_handler(
                        session_id,
                        transcribed_text,
                        interview_state,
                        job_id
                    )
                else:
                    # Interview not started yet - don't auto-submit
                    st.warning("Please start the interview before submitting answers.")
                    interview_state["recording_state"] = "idle"
            return
            
        except APIError as e:
            last_error = e
            # Check if we should retry
            if _is_retryable_error(e) and attempt < max_retries:
                delay = BASE_DELAY * (2 ** attempt)
                time.sleep(delay)
                continue
            
            # Non-retryable error or exhausted retries
            interview_state["recording_state"] = "error"
            interview_state["transcription_error"] = str(e)
            interview_state["retry_attempt"] = 0
            st.error(f"Transcription failed: {str(e)}")
            return
            
        except Exception as e:
            interview_state["recording_state"] = "error"
            interview_state["transcription_error"] = str(e)
            interview_state["retry_attempt"] = 0
            st.error(f"Unexpected error during transcription: {str(e)}")
            return
    
    # Should not reach here, but handle just in case
    if last_error:
        interview_state["recording_state"] = "error"
        interview_state["transcription_error"] = str(last_error)
        interview_state["retry_attempt"] = 0
        st.error(f"Transcription failed after {max_retries} retries: {str(last_error)}")
