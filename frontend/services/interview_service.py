"""Interview service for handling interview operations."""
import streamlit as st
from api_client import start_interview, submit_answer, end_interview, APIError


def start_interview_handler(job_id: str, interview_state: dict) -> None:
    """
    Handle starting an interview.
    
    Args:
        job_id: ID of the job
        interview_state: Dictionary containing interview state (modified in place)
    """
    try:
        result = start_interview(job_id)
        interview_state["interview_started"] = True
        interview_state["session_id"] = result["session_id"]
        interview_state["current_question"] = result["question"]
        interview_state["question_number"] = result["question_number"]
        interview_state["conversation_history"] = result.get("conversation_history", [])
        interview_state["interview_complete"] = False
        st.rerun()
    except APIError as e:
        st.error(f"Failed to start interview: {str(e)}")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")


def submit_answer_handler(session_id: str, answer: str, interview_state: dict, job_id: str = None) -> None:
    """
    Handle submitting an answer.
    
    Args:
        session_id: Session identifier
        answer: User's answer text
        interview_state: Dictionary containing interview state (modified in place)
        job_id: Optional job ID (if not provided, uses selected_job_id from session state)
    """
    if not session_id:
        st.error("Cannot submit answer: Interview session not started.")
        return
    
    # Use provided job_id or fall back to session state
    if job_id is None:
        job_id = st.session_state.get("selected_job_id")
    
    try:
        result = submit_answer(session_id, answer)
        
        # Sync conversation history from backend (single source of truth)
        interview_state["conversation_history"] = result["conversation_history"]
        
        # Update state with next question
        interview_state["current_question"] = result["question"]
        interview_state["question_number"] = result["question_number"]
        interview_state["interview_complete"] = result["interview_complete"]
        
        if result["interview_complete"]:
            st.success("Interview completed! Thank you for your responses.")
            # Store session_id for results page
            st.session_state["completed_session_id"] = interview_state["session_id"]
            st.session_state["completed_job_id"] = job_id
            # Navigate to results page
            st.session_state["current_page"] = "interview_results"
        
        # Rerun once to update UI or navigate
        st.rerun()
    except APIError as e:
        st.error(f"Failed to submit answer: {str(e)}")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")


def end_interview_handler(session_id: str, interview_state: dict, job_id: str = None) -> None:
    """
    Handle ending an interview.
    
    Args:
        session_id: Session identifier
        interview_state: Dictionary containing interview state (modified in place)
        job_id: Optional job ID (if not provided, uses selected_job_id from session state)
    """
    if not session_id:
        st.error("Cannot end interview: No active session.")
        return
    
    # Use provided job_id or fall back to session state
    if job_id is None:
        job_id = st.session_state.get("selected_job_id")
    
    try:
        end_interview(session_id)
        
        # Store session_id for results page
        st.session_state["completed_session_id"] = session_id
        st.session_state["completed_job_id"] = job_id
        
        # Navigate to results page
        st.session_state["current_page"] = "interview_results"
        st.rerun()
    except APIError as e:
        st.error(f"Failed to end interview: {str(e)}")
        # Only navigate if we have a valid session_id
        if session_id:
            st.session_state["completed_session_id"] = session_id
            st.session_state["completed_job_id"] = job_id
            st.session_state["current_page"] = "interview_results"
            st.rerun()
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        # Only navigate if we have a valid session_id
        if session_id:
            st.session_state["completed_session_id"] = session_id
            st.session_state["completed_job_id"] = job_id
            st.session_state["current_page"] = "interview_results"
            st.rerun()

