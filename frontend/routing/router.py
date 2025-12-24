"""Routing module for page navigation."""
import streamlit as st
from models.job import Job
from frontend.pages.job_listing import render_job_listing
from frontend.pages.interview_room import render_interview_room
from frontend.pages.interview_results import render_interview_results


def route_to_page(jobs: list[Job]) -> None:
    """
    Route to the appropriate page based on current_page in session state.
    
    Args:
        jobs: List of Job instances
    """
    current_page = st.session_state.get("current_page", "job_listing")
    
    if current_page == "job_listing":
        render_job_listing(jobs)
    elif current_page == "interview_room":
        # Find selected job
        selected_job = next(
            (job for job in jobs if job.id == st.session_state.get("selected_job_id")),
            None
        )
        if selected_job:
            render_interview_room(selected_job)
        else:
            st.error("Job not found. Returning to job listings.")
            st.session_state["current_page"] = "job_listing"
            st.session_state["selected_job_id"] = None
            st.rerun()
    elif current_page == "interview_results":
        # Find job for completed session
        completed_job_id = st.session_state.get("completed_job_id")
        completed_session_id = st.session_state.get("completed_session_id")
        
        if not completed_session_id:
            st.error("No session ID provided. Returning to job listings.")
            st.session_state["current_page"] = "job_listing"
            st.rerun()
            return
        
        completed_job = next(
            (job for job in jobs if job.id == completed_job_id),
            None
        )
        
        if completed_job:
            render_interview_results(completed_session_id, completed_job)
        else:
            st.error("Job not found. Returning to job listings.")
            st.session_state["current_page"] = "job_listing"
            st.session_state["completed_session_id"] = None
            st.session_state["completed_job_id"] = None
            st.rerun()

