"""Tests for question generator service."""
import pytest
from unittest.mock import patch, MagicMock
from backend.services.question_generator import QuestionGenerator
from models.job import Job


def test_generate_question_initial():
    """Test that initial question is generated and is role-grounded."""
    job = Job(
        id="job_1",
        title="Software Engineer",
        description="Build software",
        department="Engineering",
        location="Remote",
        requirements=["Python", "FastAPI"]
    )
    
    with patch("backend.services.question_generator.dspy") as mock_dspy:
        mock_result = MagicMock()
        mock_result.question = "Why are you interested in this Software Engineer position in Engineering?"
        mock_result.is_followup = False
        
        mock_interviewer = MagicMock()
        mock_interviewer.return_value = mock_result
        mock_dspy.ChainOfThought.return_value = mock_interviewer
        mock_dspy.History.return_value = MagicMock()
        
        generator = QuestionGenerator(job)
        question, is_followup = generator.generate_question("")
        
        assert isinstance(question, str)
        assert len(question) > 0
        assert isinstance(is_followup, bool)
        assert is_followup is False
        # Should contain job-specific keywords
        assert "Software Engineer" in question or "Engineering" in question


def test_generate_question_with_empty_requirements():
    """Test question generation with empty requirements."""
    job = Job(
        id="job_1",
        title="Manager",
        description="Manage team",
        department="Management",
        location="Remote",
        requirements=[]
    )
    
    with patch("backend.services.question_generator.dspy") as mock_dspy:
        mock_result = MagicMock()
        mock_result.question = "Why are you interested in this Manager position in Management?"
        mock_result.is_followup = False
        
        mock_interviewer = MagicMock()
        mock_interviewer.return_value = mock_result
        mock_dspy.ChainOfThought.return_value = mock_interviewer
        mock_dspy.History.return_value = MagicMock()
        
        generator = QuestionGenerator(job)
        question, is_followup = generator.generate_question("")
        
        assert isinstance(question, str)
        assert len(question) > 0
        assert "Manager" in question or "Management" in question


def test_generate_question_with_answer():
    """Test that question is generated with candidate answer and returns tuple with is_followup."""
    job = Job(
        id="job_1",
        title="Software Engineer",
        description="Build software",
        department="Engineering",
        location="Remote",
        requirements=["Python", "FastAPI"]
    )
    
    with patch("backend.services.question_generator.dspy") as mock_dspy:
        mock_result = MagicMock()
        mock_result.question = "Tell me about your Python experience"
        mock_result.is_followup = False
        
        mock_interviewer = MagicMock()
        mock_interviewer.return_value = mock_result
        mock_dspy.ChainOfThought.return_value = mock_interviewer
        mock_history = MagicMock()
        mock_dspy.History.return_value = mock_history
        
        generator = QuestionGenerator(job)
        question, is_followup = generator.generate_question("I love coding")
        
        assert isinstance(question, str)
        assert len(question) > 0
        assert isinstance(is_followup, bool)
        # Verify interviewer was called with history and candidate_answer
        mock_interviewer.assert_called_once()


def test_generate_question_incorporates_job_info():
    """Test that question incorporates job information."""
    job = Job(
        id="job_1",
        title="Data Scientist",
        description="Analyze data",
        department="Data",
        location="Remote",
        requirements=["Python", "Machine Learning"]
    )
    
    with patch("backend.services.question_generator.dspy") as mock_dspy:
        mock_result = MagicMock()
        mock_result.question = "What is your experience with Data Science and Machine Learning?"
        mock_result.is_followup = False
        
        mock_interviewer = MagicMock()
        mock_interviewer.return_value = mock_result
        mock_dspy.ChainOfThought.return_value = mock_interviewer
        mock_dspy.History.return_value = MagicMock()
        
        generator = QuestionGenerator(job)
        question, is_followup = generator.generate_question("")
        
        assert isinstance(question, str)
        assert isinstance(is_followup, bool)
        # Should contain job-specific keywords
        assert "Data Scientist" in question or "Data" in question or "Python" in question or "Machine Learning" in question


def test_generate_question_sequencing():
    """Test that questions are sequenced correctly."""
    job = Job(
        id="job_1",
        title="Engineer",
        description="Build",
        department="Eng",
        location="Remote",
        requirements=["Python"]
    )
    
    with patch("backend.services.question_generator.dspy") as mock_dspy:
        mock_interviewer = MagicMock()
        mock_dspy.ChainOfThought.return_value = mock_interviewer
        mock_history = MagicMock()
        mock_dspy.History.return_value = mock_history
        
        # Set up different return values for each call
        mock_results = [
            MagicMock(question="Question 1", is_followup=False),
            MagicMock(question="Question 2", is_followup=False),
            MagicMock(question="Question 3", is_followup=True),
        ]
        mock_interviewer.side_effect = mock_results
        
        generator = QuestionGenerator(job)
        
        # Generate multiple questions
        q1, f1 = generator.generate_question("")
        q2, f2 = generator.generate_question("Answer 1")
        q3, f3 = generator.generate_question("Answer 2")
        
        # All should be valid questions
        assert all(isinstance(q, str) and len(q) > 0 for q in [q1, q2, q3])
        assert all(isinstance(f, bool) for f in [f1, f2, f3])
        # Questions should be different
        assert q1 != q2
        assert q2 != q3


def test_generate_questions_role_grounded():
    """Test that questions are role-grounded for different jobs."""
    job1 = Job(
        id="job_1",
        title="Product Manager",
        description="Manage products",
        department="Product",
        location="Remote",
        requirements=["Strategy", "Agile"]
    )
    
    job2 = Job(
        id="job_2",
        title="Data Scientist",
        description="Analyze data",
        department="Data",
        location="Remote",
        requirements=["Python", "ML"]
    )
    
    with patch("backend.services.question_generator.dspy") as mock_dspy:
        mock_interviewer = MagicMock()
        mock_dspy.ChainOfThought.return_value = mock_interviewer
        mock_dspy.History.return_value = MagicMock()
        
        # Set up different return values for different jobs
        mock_interviewer.side_effect = [
            MagicMock(question="Why are you interested in Product Management and Strategy?", is_followup=False),
            MagicMock(question="What is your experience with Data Science and Python?", is_followup=False),
        ]
        
        generator1 = QuestionGenerator(job1)
        generator2 = QuestionGenerator(job2)
        
        q1, _ = generator1.generate_question("")
        q2, _ = generator2.generate_question("")
        
        # Questions should reflect different jobs
        assert "Product Manager" in q1 or "Product" in q1 or "Strategy" in q1
        assert "Data Scientist" in q2 or "Data" in q2 or "Python" in q2 or "ML" in q2


def test_generate_question_returns_followup_flag():
    """Test that generate_question returns is_followup boolean."""
    job = Job(
        id="job_1",
        title="Engineer",
        description="Build",
        department="Eng",
        location="Remote",
        requirements=["Python"]
    )
    
    with patch("backend.services.question_generator.dspy") as mock_dspy:
        mock_result = MagicMock()
        mock_result.question = "Can you tell me more about your web development experience?"
        mock_result.is_followup = True
        
        mock_interviewer = MagicMock()
        mock_interviewer.return_value = mock_result
        mock_dspy.ChainOfThought.return_value = mock_interviewer
        mock_dspy.History.return_value = MagicMock()
        
        generator = QuestionGenerator(job)
        question, is_followup = generator.generate_question("I use Python for web development")
        
        assert isinstance(question, str)
        assert isinstance(is_followup, bool)
        assert is_followup is True


def test_generate_question_initial_always_standalone():
    """Test that initial question (empty input) is always standalone (not a follow-up)."""
    job = Job(
        id="job_1",
        title="Engineer",
        description="Build",
        department="Eng",
        location="Remote",
        requirements=["Python"]
    )
    
    with patch("backend.services.question_generator.dspy") as mock_dspy:
        mock_result = MagicMock()
        mock_result.question = "Why are you interested in this position?"
        mock_result.is_followup = False
        
        mock_interviewer = MagicMock()
        mock_interviewer.return_value = mock_result
        mock_dspy.ChainOfThought.return_value = mock_interviewer
        mock_dspy.History.return_value = MagicMock()
        
        generator = QuestionGenerator(job)
        question, is_followup = generator.generate_question("")
        
        assert isinstance(question, str)
        assert len(question) > 0
        assert is_followup is False
