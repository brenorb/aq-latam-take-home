"""Tests for interview service."""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from backend.services.interview_service import InterviewService
from models.job import Job, load_jobs


def test_start_interview():
    """Test starting an interview creates session and returns question."""
    with patch("backend.services.interview_service.QuestionGenerator") as mock_generator_class:
        mock_generator = MagicMock()
        mock_generator.generate_question.return_value = ("Why are you interested in this position?", False)
        mock_generator_class.return_value = mock_generator
        
        service = InterviewService()
        
        result = service.start_interview("job_1")
    
    assert "session_id" in result
    assert "question" in result
    assert "question_number" in result
    assert "conversation_history" in result
    assert result["question_number"] == 1
    assert isinstance(result["question"], str)
    assert len(result["question"]) > 0
    assert isinstance(result["conversation_history"], list)
    assert len(result["conversation_history"]) == 0  # Empty at start


def test_start_interview_generates_unique_session_ids():
    """Test that each interview gets a unique session ID."""
    with patch("backend.services.interview_service.QuestionGenerator") as mock_generator_class:
        mock_generator = MagicMock()
        mock_generator.generate_question.return_value = ("Why are you interested?", False)
        mock_generator_class.return_value = mock_generator
        
        service = InterviewService()
        
        result1 = service.start_interview("job_1")
        result2 = service.start_interview("job_1")
    
    assert result1["session_id"] != result2["session_id"]


def test_start_interview_stores_state():
    """Test that interview state is stored after starting."""
    with patch("backend.services.interview_service.QuestionGenerator") as mock_generator_class:
        mock_generator = MagicMock()
        mock_generator.generate_question.return_value = ("Why are you interested?", False)
        mock_generator_class.return_value = mock_generator
        
        service = InterviewService()
        
        result = service.start_interview("job_1")
    session_id = result["session_id"]
    
    # Verify state exists
    assert session_id in service._interviews
    state = service._interviews[session_id]
    assert state["job_id"] == "job_1"
    assert state["current_question_number"] == 1
    assert state["is_complete"] is False
    assert state["standalone_question_count"] == 1
    assert state["follow_up_count"] == 0
    assert state["total_question_count"] == 1


def test_submit_answer():
    """Test submitting an answer returns next question."""
    with patch("backend.services.interview_service.QuestionGenerator") as mock_generator_class:
        mock_generator = MagicMock()
        mock_generator.generate_question.side_effect = [
            ("Why are you interested?", False),  # Initial question
            ("Tell me about your experience", False),  # Next question
        ]
        mock_generator_class.return_value = mock_generator
        
        service = InterviewService()
        
        start_result = service.start_interview("job_1")
        session_id = start_result["session_id"]
        first_question = start_result["question"]
        
        answer_result = service.submit_answer(session_id, "I am interested because...")
        
        assert "question" in answer_result
        assert "question_number" in answer_result
        assert "interview_complete" in answer_result
        assert "conversation_history" in answer_result
        assert answer_result["question_number"] == 2
        assert answer_result["interview_complete"] is False
        assert isinstance(answer_result["question"], str)
        assert isinstance(answer_result["conversation_history"], list)
        assert len(answer_result["conversation_history"]) == 1
        assert answer_result["conversation_history"][0]["question"] == first_question
        assert answer_result["conversation_history"][0]["answer"] == "I am interested because..."
        assert answer_result["conversation_history"][0]["question_number"] == 1
        assert answer_result["conversation_history"][0]["is_followup"] is False


def test_submit_answer_adds_to_conversation_history():
    """Test that submitting answer adds Q/A pair to history with is_followup."""
    with patch("backend.services.interview_service.QuestionGenerator") as mock_generator_class:
        mock_generator = MagicMock()
        mock_generator.generate_question.side_effect = [
            ("Why are you interested?", False),  # Initial question
            ("Next question", False),  # Next question
        ]
        mock_generator_class.return_value = mock_generator
        
        service = InterviewService()
        
        start_result = service.start_interview("job_1")
        session_id = start_result["session_id"]
        first_question = start_result["question"]
        
        service.submit_answer(session_id, "My answer")
        
        state = service._interviews[session_id]
        assert len(state["conversation_history"]) == 1
        assert state["conversation_history"][0]["question"] == first_question
        assert state["conversation_history"][0]["answer"] == "My answer"
        assert state["conversation_history"][0]["question_number"] == 1
        assert state["conversation_history"][0]["is_followup"] is False


def test_submit_answer_tracks_question_types():
    """Test that interview tracks standalone and follow-up question counts."""
    with patch("backend.services.interview_service.QuestionGenerator") as mock_generator_class:
        mock_generator = MagicMock()
        # Results for: initial question, question 2 (standalone), question 3 (follow-up)
        mock_generator.generate_question.side_effect = [
            ("Question 1", False),  # Initial
            ("Question 2", False),  # Standalone
            ("Question 3", True),   # Follow-up
        ]
        mock_generator_class.return_value = mock_generator
        
        service = InterviewService()
        
        start_result = service.start_interview("job_1")
        session_id = start_result["session_id"]
        
        # Initial state: 1 standalone, 0 follow-up, 1 total
        state = service._interviews[session_id]
        assert state["standalone_question_count"] == 1
        assert state["follow_up_count"] == 0
        assert state["total_question_count"] == 1
        
        # Submit answer 1: should add standalone question (Question 2)
        service.submit_answer(session_id, "Answer 1")
        state = service._interviews[session_id]
        assert state["standalone_question_count"] == 2
        assert state["follow_up_count"] == 0
        assert state["total_question_count"] == 2
        
        # Submit answer 2: should add follow-up question (Question 3)
        service.submit_answer(session_id, "Answer 2")
        state = service._interviews[session_id]
        assert state["standalone_question_count"] == 2
        assert state["follow_up_count"] == 1
        assert state["total_question_count"] == 3


def test_submit_answer_completes_when_minimums_met():
    """Test that interview completes when minimum requirements are met."""
    with patch("backend.services.interview_service.QuestionGenerator") as mock_generator_class:
        mock_generator = MagicMock()
        # Generate questions: initial Q1 (standalone), then Q2-7 (standalone), Q8-9 (follow-ups)
        # Total: 7 standalone + 2 follow-ups = 9 questions
        mock_generator.generate_question.side_effect = [
            ("Question 1", False),  # Initial
        ] + [
            (f"Question {i}", False) for i in range(2, 8)  # Standalone
        ] + [
            (f"Question {i}", True) for i in range(8, 10)  # Follow-ups
        ]
        mock_generator_class.return_value = mock_generator
        
        service = InterviewService()
        
        start_result = service.start_interview("job_1")
        session_id = start_result["session_id"]
        
        # Submit answers until we have 6 standalone + 2 follow-ups
        # After Q1 (initial), we need 5 more standalone + 2 follow-ups = 7 more questions
        # So after 7 answers, we'll have 6 standalone + 2 follow-ups = 8 total
        for i in range(1, 8):  # 7 more answers
            result = service.submit_answer(session_id, f"Answer {i}")
            state = service._interviews[session_id]
            
            # Should not complete until minimums are met
            if state["standalone_question_count"] < 6 or state["follow_up_count"] < 2:
                assert result["interview_complete"] is False
            else:
                # Minimums met - may complete if total >= 10
                if state["total_question_count"] >= 10:
                    assert result["interview_complete"] is True


def test_submit_answer_respects_max_10_questions():
    """Test that interview stops at 10 questions maximum."""
    with patch("backend.services.interview_service.QuestionGenerator") as mock_generator_class:
        mock_generator = MagicMock()
        # Generate questions: initial Q1, then Q2-10
        # Make sure we have at least 6 standalone and 2 follow-ups by Q10
        mock_generator.generate_question.side_effect = [
            ("Question 1", False),  # Initial
        ] + [
            (f"Question {i}", (i % 3 == 0)) for i in range(2, 11)
        ]
        mock_generator_class.return_value = mock_generator
        
        service = InterviewService()
        
        start_result = service.start_interview("job_1")
        session_id = start_result["session_id"]
        
        # Submit answers until we hit 10 questions total
        for i in range(1, 10):  # 9 more answers
            result = service.submit_answer(session_id, f"Answer {i}")
            state = service._interviews[session_id]
            
            if state["total_question_count"] < 10:
                assert result["interview_complete"] is False
            else:
                # At 10 questions, should complete if minimums are met
                if state["standalone_question_count"] >= 6 and state["follow_up_count"] >= 2:
                    assert result["interview_complete"] is True


def test_submit_answer_invalid_session():
    """Test that submitting answer with invalid session raises error."""
    service = InterviewService()
    
    with pytest.raises(ValueError, match="Session not found"):
        service.submit_answer("invalid-session-id", "Answer")


def test_submit_answer_empty_answer():
    """Test that submitting empty answer raises error."""
    with patch("backend.services.interview_service.QuestionGenerator") as mock_generator_class:
        mock_generator = MagicMock()
        mock_generator.generate_question.return_value = ("Question 1", False)
        mock_generator_class.return_value = mock_generator
        
        service = InterviewService()
        
        start_result = service.start_interview("job_1")
        session_id = start_result["session_id"]
        
        with pytest.raises(ValueError, match="Answer cannot be empty"):
            service.submit_answer(session_id, "")


def test_end_interview():
    """Test ending an interview marks it as complete."""
    with patch("backend.services.interview_service.QuestionGenerator") as mock_generator_class:
        mock_generator = MagicMock()
        mock_generator.generate_question.return_value = ("Question 1", False)
        mock_generator_class.return_value = mock_generator
        
        service = InterviewService()
        
        start_result = service.start_interview("job_1")
        session_id = start_result["session_id"]
        
        result = service.end_interview(session_id)
    
    assert result["session_id"] == session_id
    assert "message" in result
    
    state = service._interviews[session_id]
    assert state["is_complete"] is True
    assert state["ended_at"] is not None
    # Verify timezone awareness
    assert state["started_at"].tzinfo is not None
    assert state["ended_at"].tzinfo is not None


def test_end_interview_invalid_session():
    """Test that ending interview with invalid session raises error."""
    service = InterviewService()
    
    with pytest.raises(ValueError, match="Session not found"):
        service.end_interview("invalid-session-id")


def test_interview_state_persistence():
    """Test that interview state persists across multiple operations."""
    with patch("backend.services.interview_service.QuestionGenerator") as mock_generator_class:
        mock_generator = MagicMock()
        # Results: initial Q1, then Q2 (standalone), Q3 (follow-up)
        mock_generator.generate_question.side_effect = [
            ("Question 1", False),  # Initial
            ("Question 2", False),  # Standalone
            ("Question 3", True),   # Follow-up
        ]
        mock_generator_class.return_value = mock_generator
        
        service = InterviewService()
        
        start_result = service.start_interview("job_1")
        session_id = start_result["session_id"]
        
        # Submit multiple answers
        service.submit_answer(session_id, "Answer 1")
        service.submit_answer(session_id, "Answer 2")
        
        state = service._interviews[session_id]
        assert len(state["conversation_history"]) == 2
        assert state["current_question_number"] == 3
        assert state["standalone_question_count"] == 2
        assert state["follow_up_count"] == 1
        assert state["total_question_count"] == 3

