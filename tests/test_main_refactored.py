"""Tests for refactored main.py."""
import pytest
from unittest.mock import MagicMock
from models.job import Job
import json


def test_main_initializes_navigation_state(mocker):
    """Test that main() initializes navigation state."""
    mock_st = mocker.patch('main.st')
    mock_st.session_state = {}
    mock_st.error = MagicMock()
    
    mock_initialize_navigation_state = mocker.patch('main.initialize_navigation_state')
    mocker.patch('main.load_jobs', return_value=[])
    mocker.patch('main.route_to_page')
    
    from main import main
    main()
    
    mock_initialize_navigation_state.assert_called_once()


def test_main_loads_jobs(mocker):
    """Test that main() loads jobs via load_jobs()."""
    mock_st = mocker.patch('main.st')
    mock_st.session_state = {}
    mock_st.error = MagicMock()
    
    mocker.patch('main.initialize_navigation_state')
    mock_load_jobs = mocker.patch('main.load_jobs', return_value=[])
    mock_route_to_page = mocker.patch('main.route_to_page')
    
    from main import main
    main()
    
    mock_load_jobs.assert_called_once()
    mock_route_to_page.assert_called_once_with([])


def test_main_calls_route_to_page_with_jobs(mocker):
    """Test that main() calls route_to_page() with loaded jobs."""
    mock_st = mocker.patch('main.st')
    mock_st.session_state = {}
    mock_st.error = MagicMock()
    
    mocker.patch('main.initialize_navigation_state')
    
    jobs = [
        Job(id="job_1", title="Engineer", description="Build", 
            department="Eng", location="Remote", requirements=["Python"]),
    ]
    mocker.patch('main.load_jobs', return_value=jobs)
    mock_route_to_page = mocker.patch('main.route_to_page')
    
    from main import main
    main()
    
    mock_route_to_page.assert_called_once_with(jobs)


def test_main_handles_file_not_found_error(mocker):
    """Test that main() handles FileNotFoundError for missing jobs.json."""
    mock_st = mocker.patch('main.st')
    mock_st.session_state = {}
    mock_st.error = MagicMock()
    
    mocker.patch('main.initialize_navigation_state')
    mocker.patch('main.load_jobs', side_effect=FileNotFoundError("File not found"))
    mock_route_to_page = mocker.patch('main.route_to_page')
    
    from main import main
    main()
    
    assert mock_st.error.called
    # Should not call route_to_page on error
    assert not mock_route_to_page.called


def test_main_handles_json_decode_error(mocker):
    """Test that main() handles JSONDecodeError."""
    mock_st = mocker.patch('main.st')
    mock_st.session_state = {}
    mock_st.error = MagicMock()
    
    mocker.patch('main.initialize_navigation_state')
    mocker.patch('main.load_jobs', side_effect=json.JSONDecodeError("Invalid JSON", "", 0))
    
    from main import main
    main()
    
    assert mock_st.error.called


def test_main_handles_value_error(mocker):
    """Test that main() handles ValueError."""
    mock_st = mocker.patch('main.st')
    mock_st.session_state = {}
    mock_st.error = MagicMock()
    
    mocker.patch('main.initialize_navigation_state')
    mocker.patch('main.load_jobs', side_effect=ValueError("Invalid data"))
    
    from main import main
    main()
    
    assert mock_st.error.called


def test_main_handles_type_error(mocker):
    """Test that main() handles TypeError."""
    mock_st = mocker.patch('main.st')
    mock_st.session_state = {}
    mock_st.error = MagicMock()
    
    mocker.patch('main.initialize_navigation_state')
    mocker.patch('main.load_jobs', side_effect=TypeError("Type error"))
    
    from main import main
    main()
    
    assert mock_st.error.called

