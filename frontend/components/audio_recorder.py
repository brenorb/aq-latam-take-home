"""Audio recorder component using audio-recorder-streamlit."""
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from frontend.services.transcription_service import process_audio_from_bytes


def render_audio_recorder(job_id: str, interview_state: dict) -> None:
    """
    Render audio recorder component using audio-recorder-streamlit library.
    
    When audio is recorded, it's automatically processed for transcription.
    
    Args:
        job_id: Job ID for unique element tracking
        interview_state: Dictionary containing interview state (modified in place)
    """
    # Session state key to track last processed audio
    last_audio_key = f"last_audio_{job_id}"
    
    # Initialize session state
    if last_audio_key not in st.session_state:
        st.session_state[last_audio_key] = None
    
    # Render the audio recorder widget
    audio_bytes = audio_recorder(
        pause_threshold=2.0,  # Auto-stop after 2s silence
        sample_rate=44100,
        text="Click to record",
        recording_color="#ff4444",
        neutral_color="#6aa36f",
        icon_size="2x",
        key=f"audio_recorder_{job_id}",
    )
    
    # Process audio when returned (and it's new audio, not previously processed)
    if audio_bytes and len(audio_bytes) > 0:
        # Check if this is new audio (not already processed)
        if audio_bytes != st.session_state.get(last_audio_key):
            # Mark this audio as being processed
            st.session_state[last_audio_key] = audio_bytes
            # Process the audio for transcription
            process_audio_from_bytes(audio_bytes, job_id, interview_state)
