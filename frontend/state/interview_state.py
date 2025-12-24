"""Interview state management."""
import os

import streamlit as st


def get_interview_state(job_id: str) -> dict:
    """
    Get or initialize interview state for a specific job.
    
    Args:
        job_id: ID of the job
        
    Returns:
        Dictionary containing interview state
    """
    state_key = f"interview_state_{job_id}"
    
    if state_key not in st.session_state:
        # Initialize debug_mode from environment variable
        debug_mode = os.getenv("DEBUG_MODE", "").lower() in ("true", "1", "yes")
        
        st.session_state[state_key] = {
            "interview_started": False,
            "session_id": None,
            "conversation_history": [],
            "current_question": None,
            "question_number": 0,
            "interview_complete": False,
            "answer_text": "",
            "debug_mode": debug_mode,
            "recording_state": "idle",
            "transcribed_text": "",
            "transcription_error": None,
            "retry_attempt": 0,
            "max_retries": 3,
        }
    
    return st.session_state[state_key]

