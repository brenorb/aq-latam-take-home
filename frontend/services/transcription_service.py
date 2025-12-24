"""Transcription service for handling audio transcription."""
import streamlit as st
from api_client import transcribe_audio, APIError
from frontend.services.interview_service import submit_answer_handler


def process_audio_transcription(uploaded_file, job_id: str, interview_state: dict) -> None:
    """
    Process audio file transcription.
    
    Args:
        uploaded_file: Uploaded audio file from Streamlit file_uploader
        job_id: ID of the job
        interview_state: Dictionary containing interview state (modified in place)
    """
    try:
        # Update state to processing
        interview_state["recording_state"] = "processing"
        interview_state["transcription_error"] = None
        
        # Read audio file bytes
        audio_bytes = uploaded_file.read()
        filename = uploaded_file.name if hasattr(uploaded_file, 'name') else "audio.webm"
        
        # Call transcription API
        transcribed_text = transcribe_audio(audio_bytes, filename)
        
        # Update state with transcribed text
        interview_state["transcribed_text"] = transcribed_text
        interview_state["recording_state"] = "idle"
        
        # Clear uploaded file from session state (Streamlit handles this automatically,
        # but we can also clear it explicitly)
        upload_key = f"audio_upload_{job_id}"
        if upload_key in st.session_state:
            st.session_state[upload_key] = None
        
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
    except APIError as e:
        interview_state["recording_state"] = "error"
        interview_state["transcription_error"] = str(e)
        st.error(f"Transcription failed: {str(e)}")
    except Exception as e:
        interview_state["recording_state"] = "error"
        interview_state["transcription_error"] = str(e)
        st.error(f"Unexpected error during transcription: {str(e)}")

