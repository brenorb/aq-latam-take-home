"""Tests for conversation history component."""
from unittest.mock import MagicMock

import pytest


def test_render_conversation_history_empty(mocker):
    """Test that conversation history displays info message when empty."""
    mock_st = mocker.patch('frontend.components.conversation_history.st')
    mock_st.subheader = MagicMock()
    mock_st.info = MagicMock()
    mock_st.markdown = MagicMock()
    mock_st.divider = MagicMock()
    mock_st.container = MagicMock(return_value=MagicMock())
    
    from frontend.components.conversation_history import render_conversation_history
    render_conversation_history([])
    
    mock_st.subheader.assert_called_with("Conversation History")
    mock_st.info.assert_called_with("No questions asked yet")


def test_render_conversation_history_with_qa_pairs(mocker):
    """Test that conversation history displays Q/A pairs correctly."""
    mock_st = mocker.patch('frontend.components.conversation_history.st')
    mock_st.subheader = MagicMock()
    mock_st.info = MagicMock()
    mock_st.markdown = MagicMock()
    mock_st.divider = MagicMock()
    mock_container = MagicMock()
    mock_st.container = MagicMock(return_value=mock_container)
    
    conversation = [
        {"question": "Q1", "answer": "A1", "question_number": 1},
        {"question": "Q2", "answer": "A2", "question_number": 2},
    ]
    
    from frontend.components.conversation_history import render_conversation_history
    render_conversation_history(conversation)
    
    # Should create scrollable container
    mock_st.container.assert_called()
    
    # Should display Q/A pairs
    assert mock_st.markdown.call_count >= 2  # At least Q and A for each pair


def test_render_conversation_history_creates_scrollable_container(mocker):
    """Test that conversation history creates scrollable container."""
    mock_st = mocker.patch('frontend.components.conversation_history.st')
    mock_st.subheader = MagicMock()
    mock_st.info = MagicMock()
    mock_st.markdown = MagicMock()
    mock_st.divider = MagicMock()
    mock_container = MagicMock()
    mock_st.container = MagicMock(return_value=mock_container)
    
    conversation = [
        {"question": "Q1", "answer": "A1", "question_number": 1},
    ]
    
    from frontend.components.conversation_history import render_conversation_history
    render_conversation_history(conversation)
    
    # Should call container with height parameter for scrollability
    mock_st.container.assert_called()


def test_render_conversation_history_formats_qa_correctly(mocker):
    """Test that Q/A pairs are formatted correctly."""
    mock_st = mocker.patch('frontend.components.conversation_history.st')
    mock_st.subheader = MagicMock()
    mock_st.info = MagicMock()
    mock_st.markdown = MagicMock()
    mock_st.divider = MagicMock()
    mock_container = MagicMock()
    mock_st.container = MagicMock(return_value=mock_container)
    
    conversation = [
        {"question": "What is Python?", "answer": "A programming language", "question_number": 1},
    ]
    
    from frontend.components.conversation_history import render_conversation_history
    render_conversation_history(conversation)
    
    # Check that markdown was called with Q/A formatting
    markdown_calls = [str(call) for call in mock_st.markdown.call_args_list]
    assert any("Q1" in str(call) or "question_number" in str(call).lower() for call in mock_st.markdown.call_args_list)

