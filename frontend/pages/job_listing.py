"""Job listing page."""
import streamlit as st
from models.job import Job


def render_job_listing(jobs: list[Job]) -> None:
    """
    Render the job listing page displaying all available positions.
    
    Shows each job's title, department, location, description, and requirements.
    Each job has a button to start an interview, which navigates to the interview room.
    
    Args:
        jobs: List of Job instances to display
    """
    st.title("Available Positions")
    st.write("Select a job to start your interview:")
    
    for job in jobs:
        with st.container():
            st.subheader(job.title)
            st.write(f"**Department:** {job.department}")
            st.write(f"**Location:** {job.location}")
            st.write(f"**Description:** {job.description}")
            st.write(f"**Requirements:** {', '.join(job.requirements)}")
            
            if st.button(f"Start Interview - {job.title}", key=f"job_{job.id}"):
                st.session_state["selected_job_id"] = job.id
                st.session_state["current_page"] = "interview_room"
                st.rerun()

