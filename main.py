"""Main Streamlit application for AI Interviewer Platform."""
import json

import streamlit as st

from frontend.routing.router import route_to_page
from frontend.state.navigation_state import initialize_navigation_state
from models.job import load_jobs


def main() -> None:
    """
    Main application entry point.
    
    Initializes Streamlit session state for navigation and job selection,
    loads job data from JSON file, and routes to the appropriate page based
    on the current session state.
    
    Session state keys:
        current_page: Either "job_listing", "interview_room", or "interview_results"
        selected_job_id: ID of the currently selected job (None if none selected)
        completed_session_id: Session ID of completed interview (for results page)
        completed_job_id: Job ID of completed interview (for results page)
    """
    # Initialize navigation state
    initialize_navigation_state()
    
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
    route_to_page(jobs)


if __name__ == "__main__":
    main()
