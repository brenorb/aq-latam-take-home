"""Tests for router module."""
import pytest
from unittest.mock import MagicMock
from models.job import Job


def test_route_to_page_job_listing(mocker):
    """Test that routing to job_listing calls render_job_listing."""
    mock_st = mocker.patch('frontend.routing.router.st')
    mock_st.session_state = {"current_page": "job_listing"}
    
    mock_render_job_listing = mocker.patch('frontend.routing.router.render_job_listing')
    
    jobs = [
        Job(id="job_1", title="Engineer", description="Build", 
            department="Eng", location="Remote", requirements=["Python"]),
    ]
    
    from frontend.routing.router import route_to_page
    route_to_page(jobs)
    
    mock_render_job_listing.assert_called_once_with(jobs)


def test_route_to_page_interview_room(mocker):
    """Test that routing to interview_room finds job and calls render_interview_room."""
    mock_st = mocker.patch('frontend.routing.router.st')
    mock_st.session_state = {
        "current_page": "interview_room",
        "selected_job_id": "job_1"
    }
    mock_st.error = MagicMock()
    mock_st.rerun = MagicMock()
    
    mock_render_interview_room = mocker.patch('frontend.routing.router.render_interview_room')
    
    job = Job(
        id="job_1",
        title="Engineer",
        description="Build",
        department="Eng",
        location="Remote",
        requirements=["Python"]
    )
    jobs = [job]
    
    from frontend.routing.router import route_to_page
    route_to_page(jobs)
    
    mock_render_interview_room.assert_called_once_with(job)


def test_route_to_page_interview_room_job_not_found(mocker):
    """Test that routing handles error when job not found."""
    mock_st = mocker.patch('frontend.routing.router.st')
    mock_st.session_state = {
        "current_page": "interview_room",
        "selected_job_id": "job_nonexistent"
    }
    mock_st.error = MagicMock()
    mock_st.rerun = MagicMock()
    
    mock_render_interview_room = mocker.patch('frontend.routing.router.render_interview_room')
    
    jobs = [
        Job(id="job_1", title="Engineer", description="Build", 
            department="Eng", location="Remote", requirements=["Python"]),
    ]
    
    from frontend.routing.router import route_to_page
    route_to_page(jobs)
    
    # Should not call render_interview_room
    assert not mock_render_interview_room.called
    # Should show error and redirect
    assert mock_st.error.called
    assert mock_st.session_state["current_page"] == "job_listing"
    assert mock_st.rerun.called


def test_route_to_page_interview_results(mocker):
    """Test that routing to interview_results finds job/session and calls render_interview_results."""
    mock_st = mocker.patch('frontend.routing.router.st')
    mock_st.session_state = {
        "current_page": "interview_results",
        "completed_session_id": "session_123",
        "completed_job_id": "job_1"
    }
    mock_st.error = MagicMock()
    mock_st.rerun = MagicMock()
    
    mock_render_interview_results = mocker.patch('frontend.routing.router.render_interview_results')
    
    job = Job(
        id="job_1",
        title="Engineer",
        description="Build",
        department="Eng",
        location="Remote",
        requirements=["Python"]
    )
    jobs = [job]
    
    from frontend.routing.router import route_to_page
    route_to_page(jobs)
    
    mock_render_interview_results.assert_called_once_with("session_123", job)


def test_route_to_page_interview_results_missing_session_id(mocker):
    """Test that routing handles error when session_id is missing."""
    mock_st = mocker.patch('frontend.routing.router.st')
    mock_st.session_state = {
        "current_page": "interview_results",
        "completed_session_id": None,
        "completed_job_id": "job_1"
    }
    mock_st.error = MagicMock()
    mock_st.rerun = MagicMock()
    
    mock_render_interview_results = mocker.patch('frontend.routing.router.render_interview_results')
    
    jobs = [
        Job(id="job_1", title="Engineer", description="Build", 
            department="Eng", location="Remote", requirements=["Python"]),
    ]
    
    from frontend.routing.router import route_to_page
    route_to_page(jobs)
    
    # Should not call render_interview_results
    assert not mock_render_interview_results.called
    # Should show error and redirect
    assert mock_st.error.called
    assert mock_st.session_state["current_page"] == "job_listing"
    assert mock_st.rerun.called


def test_route_to_page_interview_results_job_not_found(mocker):
    """Test that routing handles error when job not found for results."""
    mock_st = mocker.patch('frontend.routing.router.st')
    mock_st.session_state = {
        "current_page": "interview_results",
        "completed_session_id": "session_123",
        "completed_job_id": "job_nonexistent"
    }
    mock_st.error = MagicMock()
    mock_st.rerun = MagicMock()
    
    mock_render_interview_results = mocker.patch('frontend.routing.router.render_interview_results')
    
    jobs = [
        Job(id="job_1", title="Engineer", description="Build", 
            department="Eng", location="Remote", requirements=["Python"]),
    ]
    
    from frontend.routing.router import route_to_page
    route_to_page(jobs)
    
    # Should not call render_interview_results
    assert not mock_render_interview_results.called
    # Should show error and redirect
    assert mock_st.error.called
    assert mock_st.session_state["current_page"] == "job_listing"
    assert mock_st.rerun.called

