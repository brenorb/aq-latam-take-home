"""Main Streamlit application for AI Interviewer Platform."""
import json
import streamlit as st
from models.job import Job, load_jobs


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


def render_interview_room(job: Job) -> None:
    """
    Render the interview room page for the selected job.
    
    Displays job details and provides a basic layout structure with placeholder
    sections for question display, answer input, and conversation history.
    Includes a back button to return to the job listing.
    
    Args:
        job: The selected Job instance to display
    """
    st.title(f"Interview Room: {job.title}")
    
    # Job information
    with st.container():
        st.subheader("Job Details")
        st.write(f"**Department:** {job.department}")
        st.write(f"**Location:** {job.location}")
        st.write(f"**Description:** {job.description}")
    
    st.divider()
    
    # Layout structure for interview components
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Question")
        st.info("AI question will appear here")
        
        st.subheader("Your Answer")
        st.text_area("Speak your answer...", key="answer_input", height=100)
    
    with col2:
        st.subheader("Conversation History")
        st.info("Q/A history will appear here")
    
    st.divider()
    
    # End interview button (placeholder)
    st.button("End Interview", disabled=True, help="Not yet functional")
    
    # Back button
    if st.button("← Back to Job Listings"):
        st.session_state["current_page"] = "job_listing"
        st.session_state["selected_job_id"] = None
        st.rerun()


def main() -> None:
    """
    Main application entry point.
    
    Initializes Streamlit session state for navigation and job selection,
    loads job data from JSON file, and routes to the appropriate page based
    on the current session state.
    
    Session state keys:
        current_page: Either "job_listing" or "interview_room"
        selected_job_id: ID of the currently selected job (None if none selected)
    """
    # Initialize session state
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "job_listing"
    if "selected_job_id" not in st.session_state:
        st.session_state["selected_job_id"] = None
    
    # Load jobs
    try:
        jobs = load_jobs()
    except FileNotFoundError:
        st.error("Jobs data file not found. Please ensure data/jobs.json exists.")
        return
    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON in jobs data file: {e}")
        return
    except (ValueError, TypeError) as e:
        st.error(f"Error loading jobs data: {e}")
        return
    
    # Route to appropriate page
    if st.session_state["current_page"] == "job_listing":
        render_job_listing(jobs)
    elif st.session_state["current_page"] == "interview_room":
        # Find selected job
        selected_job = next(
            (job for job in jobs if job.id == st.session_state["selected_job_id"]),
            None
        )
        if selected_job:
            render_interview_room(selected_job)
        else:
            st.error("Job not found. Returning to job listings.")
            st.session_state["current_page"] = "job_listing"
            st.session_state["selected_job_id"] = None
            st.rerun()


if __name__ == "__main__":
    main()
