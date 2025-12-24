"""Navigation state management."""
import streamlit as st


def initialize_navigation_state() -> None:
    """
    Initialize navigation state with default values.
    
    Only sets keys that don't already exist in session_state.
    """
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "job_listing"
    if "selected_job_id" not in st.session_state:
        st.session_state["selected_job_id"] = None
    if "completed_session_id" not in st.session_state:
        st.session_state["completed_session_id"] = None
    if "completed_job_id" not in st.session_state:
        st.session_state["completed_job_id"] = None

