"""Interview room page."""
import streamlit as st
from models.job import Job
from frontend.state.interview_state import get_interview_state
from frontend.components.question_display import render_question_display
from frontend.components.answer_input import render_answer_input
from frontend.components.conversation_history import render_conversation_history
from frontend.services.interview_service import (
    start_interview_handler,
    end_interview_handler,
)


def render_interview_room(job: Job) -> None:
    """
    Render the interview room page for the selected job.
    
    Displays complete UI layout with text input area, AI question display,
    conversation history panel, and interview controls. Integrates with FastAPI
    backend for interview orchestration.
    
    Args:
        job: The selected Job instance to display
    """
    st.title(f"Interview Room: {job.title}")
    
    # Initialize interview state
    interview_state = get_interview_state(job.id)
    
    # Job information (compact display)
    with st.expander("Job Details", expanded=False):
        st.write(f"**Department:** {job.department}")
        st.write(f"**Location:** {job.location}")
        st.write(f"**Description:** {job.description}")
        st.write(f"**Requirements:** {', '.join(job.requirements)}")
    
    st.divider()
    
    # Main interview area - two column layout
    col_left, col_right = st.columns([7, 3])
    
    with col_left:
        # Question display area
        render_question_display(interview_state)
        
        # Answer input area
        render_answer_input(job, interview_state)
    
    with col_right:
        # Conversation history panel
        render_conversation_history(interview_state["conversation_history"])
    
    st.divider()
    
    # Action buttons section
    button_col1, button_col2, button_col3 = st.columns([1, 1, 1])
    
    with button_col1:
        # Start Interview button (shown when interview hasn't started)
        if not interview_state["interview_started"]:
            if st.button("Start Interview", type="primary", use_container_width=True):
                start_interview_handler(job.id, interview_state)
    
    with button_col2:
        # Submit Answer button moved inside form (handled in answer_input component)
        pass
    
    with button_col3:
        # End Interview button (shown when interview is active)
        if interview_state["interview_started"]:
            if st.button("End Interview", type="secondary", use_container_width=True):
                end_interview_handler(interview_state["session_id"], interview_state, job.id)
    
    st.divider()
    
    # Action buttons for completed interview
    if interview_state["interview_complete"]:
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("View Results", type="primary", use_container_width=True):
                st.session_state["completed_session_id"] = interview_state["session_id"]
                st.session_state["completed_job_id"] = job.id
                st.session_state["current_page"] = "interview_results"
                st.rerun()
        with col2:
            if st.button("← Back to Job Listings", use_container_width=True):
                st.session_state["current_page"] = "job_listing"
                st.session_state["selected_job_id"] = None
                st.rerun()
    else:
        # Back button (when interview not complete)
        if st.button("← Back to Job Listings"):
            st.session_state["current_page"] = "job_listing"
            st.session_state["selected_job_id"] = None
            st.rerun()

