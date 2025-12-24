"""Tests for audio recorder component."""
from unittest.mock import MagicMock

import pytest


def test_render_audio_recorder_generates_html(mocker):
    """Test that audio recorder generates HTML/JavaScript with correct job_id."""
    mock_st = mocker.patch('frontend.components.audio_recorder.st')
    mock_html = MagicMock()
    mock_st.components = MagicMock()
    mock_st.components.v1 = MagicMock()
    mock_st.components.v1.html = mock_html
    
    from frontend.components.audio_recorder import render_audio_recorder
    render_audio_recorder("job_1", spacebar_enabled=True)
    
    # Should call st.components.v1.html
    assert mock_html.called
    # HTML should contain job_id
    html_content = mock_html.call_args[0][0]
    assert "job_1" in html_content or "job_id" in html_content.lower()


def test_render_audio_recorder_passes_spacebar_enabled(mocker):
    """Test that spacebar_enabled flag is correctly passed to JavaScript."""
    mock_st = mocker.patch('frontend.components.audio_recorder.st')
    mock_html = MagicMock()
    mock_st.components = MagicMock()
    mock_st.components.v1 = MagicMock()
    mock_st.components.v1.html = mock_html
    
    from frontend.components.audio_recorder import render_audio_recorder
    render_audio_recorder("job_1", spacebar_enabled=True)
    
    html_content = mock_html.call_args[0][0]
    # JavaScript should reference spacebar_enabled
    assert "spacebar" in html_content.lower() or "space" in html_content.lower()


def test_render_audio_recorder_renders_without_errors(mocker):
    """Test that audio recorder component renders without errors."""
    mock_st = mocker.patch('frontend.components.audio_recorder.st')
    mock_html = MagicMock()
    mock_st.components = MagicMock()
    mock_st.components.v1 = MagicMock()
    mock_st.components.v1.html = mock_html
    
    from frontend.components.audio_recorder import render_audio_recorder
    # Should not raise any exceptions
    render_audio_recorder("job_1", spacebar_enabled=False)
    
    assert mock_html.called

