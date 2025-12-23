"""Tests for evaluation service."""
import pytest
from unittest.mock import MagicMock, patch
from backend.services.evaluation_service import EvaluationService
from models.job import Job


def test_evaluation_service_evaluate():
    """Test that EvaluationService generates evaluation."""
    job = Job(
        id="job_1",
        title="Software Engineer",
        description="Build software",
        department="Engineering",
        location="Remote",
        requirements=["Python", "FastAPI"]
    )
    
    conversation_history = [
        {
            "question": "Why are you interested?",
            "answer": "I love coding and building products",
            "question_number": 1,
            "is_followup": False,
        },
        {
            "question": "Tell me about your Python experience",
            "answer": "I've been using Python for 5 years",
            "question_number": 2,
            "is_followup": True,
        }
    ]
    
    service = EvaluationService()
    
    # Mock DSPy to return structured evaluation
    with patch.object(service, '_evaluator') as mock_evaluator:
        mock_response = MagicMock()
        mock_response.strengths = ["Strong technical skills", "Good communication"]
        mock_response.concerns = ["Limited experience with FastAPI"]
        mock_response.overall_score = 85.0
        mock_evaluator.return_value = mock_response
        
        result = service.evaluate(job, conversation_history)
    
    assert "strengths" in result
    assert "concerns" in result
    assert "overall_score" in result
    assert isinstance(result["strengths"], list)
    assert isinstance(result["concerns"], list)
    assert isinstance(result["overall_score"], (int, float))
    assert 0 <= result["overall_score"] <= 100


def test_evaluation_service_implements_protocol():
    """Test that EvaluationService implements IEvaluationProvider protocol."""
    from backend.services.protocols import IEvaluationProvider
    
    service = EvaluationService()
    
    # Check that service has evaluate method with correct signature
    assert hasattr(service, "evaluate")
    assert callable(service.evaluate)


def test_evaluation_service_handles_empty_history():
    """Test that EvaluationService handles empty conversation history."""
    job = Job(
        id="job_1",
        title="Software Engineer",
        description="Build software",
        department="Engineering",
        location="Remote",
        requirements=["Python"]
    )
    
    service = EvaluationService()
    
    with patch.object(service, '_evaluator') as mock_evaluator:
        mock_response = MagicMock()
        mock_response.strengths = []
        mock_response.concerns = ["No responses provided"]
        mock_response.overall_score = 0.0
        mock_evaluator.return_value = mock_response
        
        result = service.evaluate(job, [])
    
    assert result["strengths"] == []
    assert len(result["concerns"]) > 0
    assert result["overall_score"] == 0.0

