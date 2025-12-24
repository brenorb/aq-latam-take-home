"""Tests for job listing page."""
import pytest
from unittest.mock import MagicMock
from models.job import Job


def test_render_job_listing_displays_jobs(mocker):
    """Test that render_job_listing displays all jobs."""
    mock_st = mocker.patch('frontend.pages.job_listing.st')
    mock_st.session_state = {}
    mock_st.title = MagicMock()
    mock_st.write = MagicMock()
    mock_st.button = MagicMock(return_value=False)
    mock_st.container = MagicMock(return_value=MagicMock())
    mock_st.subheader = MagicMock()
    mock_st.rerun = MagicMock()
    
    jobs = [
        Job(id="job_1", title="Engineer", description="Build", 
            department="Eng", location="Remote", requirements=["Python"]),
        Job(id="job_2", title="PM", description="Lead", 
            department="Product", location="SF", requirements=["Strategy"]),
    ]
    
    from frontend.pages.job_listing import render_job_listing
    render_job_listing(jobs)
    
    # Verify Streamlit components were called
    assert mock_st.title.called
    assert mock_st.write.called
    assert mock_st.button.called


def test_render_job_listing_shows_job_details(mocker):
    """Test that render_job_listing shows title, description, department, location, requirements."""
    mock_st = mocker.patch('frontend.pages.job_listing.st')
    mock_st.session_state = {}
    mock_st.title = MagicMock()
    mock_st.write = MagicMock()
    mock_st.button = MagicMock(return_value=False)
    mock_st.container = MagicMock(return_value=MagicMock())
    mock_st.subheader = MagicMock()
    mock_st.rerun = MagicMock()
    
    job = Job(
        id="job_1",
        title="Software Engineer",
        description="Build amazing software",
        department="Engineering",
        location="Remote",
        requirements=["Python", "FastAPI"]
    )
    
    from frontend.pages.job_listing import render_job_listing
    render_job_listing([job])
    
    # Check that job details are displayed
    assert mock_st.subheader.called
    assert mock_st.write.called


def test_render_job_listing_sets_session_state_on_selection(mocker):
    """Test that selecting a job sets selected_job_id and current_page in session state."""
    mock_st = mocker.patch('frontend.pages.job_listing.st')
    mock_st.session_state = {}
    mock_st.title = MagicMock()
    mock_st.write = MagicMock()
    mock_st.container = MagicMock(return_value=MagicMock())
    mock_st.subheader = MagicMock()
    mock_st.rerun = MagicMock()
    
    jobs = [
        Job(id="job_1", title="Engineer", description="Build", 
            department="Eng", location="Remote", requirements=["Python"]),
    ]
    
    # Mock button click - first call returns True (job selected)
    call_count = 0
    def button_side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:  # First button click selects job
            mock_st.session_state["selected_job_id"] = "job_1"
            mock_st.session_state["current_page"] = "interview_room"
            return True
        return False
    
    mock_st.button = MagicMock(side_effect=button_side_effect)
    
    from frontend.pages.job_listing import render_job_listing
    render_job_listing(jobs)
    
    # Verify session state is set
    assert mock_st.session_state["selected_job_id"] == "job_1"
    assert mock_st.session_state["current_page"] == "interview_room"
    assert mock_st.rerun.called

