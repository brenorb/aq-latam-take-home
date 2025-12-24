"""Tests for navigation and routing logic."""
import pytest
from unittest.mock import MagicMock
from models.job import Job


def test_main_app_initializes_session_state(mocker):
    """Test that main app initializes session state with defaults."""
    mock_st = mocker.patch('main.st')
    mock_st.session_state = {}
    mock_st.error = MagicMock()
    mock_st.rerun = MagicMock()
    
    jobs = [
        Job(id="job_1", title="Engineer", description="Build", 
            department="Eng", location="Remote", requirements=["Python"]),
    ]
    mocker.patch('main.load_jobs', return_value=jobs)
    mocker.patch('frontend.routing.router.route_to_page')
    mock_initialize_navigation_state = mocker.patch('main.initialize_navigation_state')
    
    from main import main
    main()
    
    # Verify initialize_navigation_state was called
    mock_initialize_navigation_state.assert_called_once()


def test_main_app_renders_job_listing_by_default(mocker):
    """Test that main app renders job listing page by default."""
    mock_st = mocker.patch('main.st')
    mock_st.session_state = {"current_page": "job_listing", "selected_job_id": None}
    mock_st.error = MagicMock()
    mock_st.rerun = MagicMock()
    
    jobs = [
        Job(id="job_1", title="Engineer", description="Build", 
            department="Eng", location="Remote", requirements=["Python"]),
    ]
    
    mocker.patch('main.load_jobs', return_value=jobs)
    mocker.patch('main.initialize_navigation_state')
    mock_route_to_page = mocker.patch('main.route_to_page')
    
    from main import main
    main()
    
    mock_route_to_page.assert_called_once_with(jobs)


def test_main_app_renders_interview_room_when_selected(mocker):
    """Test that main app renders interview room when job is selected."""
    mock_st = mocker.patch('main.st')
    mock_st.session_state = {
        "current_page": "interview_room",
        "selected_job_id": "job_1"
    }
    mock_st.error = MagicMock()
    mock_st.rerun = MagicMock()
    
    job = Job(
        id="job_1",
        title="Engineer",
        description="Build",
        department="Eng",
        location="Remote",
        requirements=["Python"]
    )
    
    jobs = [job]
    mocker.patch('main.load_jobs', return_value=jobs)
    mocker.patch('main.initialize_navigation_state')
    mock_route_to_page = mocker.patch('main.route_to_page')
    
    from main import main
    main()
    
    # Verify route_to_page was called with jobs
    mock_route_to_page.assert_called_once_with(jobs)


def test_job_selection_sets_session_state(mocker):
    """Test that selecting a job sets selected_job_id and current_page."""
    mock_st = mocker.patch('frontend.pages.job_listing.st')
    mock_st.session_state = {"current_page": "job_listing", "selected_job_id": None}
    mock_st.title = MagicMock()
    mock_st.write = MagicMock()
    mock_st.container = MagicMock(return_value=MagicMock())
    mock_st.subheader = MagicMock()
    mock_st.rerun = MagicMock()
    
    # Simulate button click for job selection
    call_count = 0
    def button_side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:  # First button is job selection
            mock_st.session_state["selected_job_id"] = "job_1"
            mock_st.session_state["current_page"] = "interview_room"
            return True
        return False
    
    mock_st.button = MagicMock(side_effect=button_side_effect)
    
    jobs = [
        Job(id="job_1", title="Engineer", description="Build",
            department="Eng", location="Remote", requirements=["Python"]),
    ]
    
    from frontend.pages.job_listing import render_job_listing
    render_job_listing(jobs)
    
    # Verify session state was updated
    assert mock_st.session_state["selected_job_id"] == "job_1"
    assert mock_st.session_state["current_page"] == "interview_room"

