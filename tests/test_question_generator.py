"""Tests for question generator service."""
import pytest
from backend.services.question_generator import QuestionGenerator
from models.job import Job


def test_generate_initial_question():
    """Test that initial question is generated and is role-grounded."""
    job = Job(
        id="job_1",
        title="Software Engineer",
        description="Build software",
        department="Engineering",
        location="Remote",
        requirements=["Python", "FastAPI"]
    )
    
    generator = QuestionGenerator()
    question = generator.generate_initial_question(job)
    
    assert isinstance(question, str)
    assert len(question) > 0
    # Should contain job-specific keywords
    assert "Software Engineer" in question or "Engineering" in question


def test_generate_initial_question_with_empty_requirements():
    """Test initial question generation with empty requirements."""
    job = Job(
        id="job_1",
        title="Manager",
        description="Manage team",
        department="Management",
        location="Remote",
        requirements=[]
    )
    
    generator = QuestionGenerator()
    question = generator.generate_initial_question(job)
    
    assert isinstance(question, str)
    assert len(question) > 0
    assert "Manager" in question or "Management" in question


def test_generate_next_question():
    """Test that next question is generated based on question number."""
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
            "answer": "I love coding",
            "question_number": 1
        }
    ]
    
    generator = QuestionGenerator()
    question = generator.generate_next_question(job, conversation_history, question_number=2)
    
    assert isinstance(question, str)
    assert len(question) > 0
    # Should be different from first question
    assert question != conversation_history[0]["question"]


def test_generate_next_question_incorporates_job_info():
    """Test that next question incorporates job information."""
    job = Job(
        id="job_1",
        title="Data Scientist",
        description="Analyze data",
        department="Data",
        location="Remote",
        requirements=["Python", "Machine Learning"]
    )
    
    generator = QuestionGenerator()
    question = generator.generate_next_question(job, [], question_number=2)
    
    assert isinstance(question, str)
    # Should contain job-specific keywords
    assert "Data Scientist" in question or "Data" in question or "Python" in question or "Machine Learning" in question


def test_generate_next_question_sequencing():
    """Test that questions are sequenced correctly."""
    job = Job(
        id="job_1",
        title="Engineer",
        description="Build",
        department="Eng",
        location="Remote",
        requirements=["Python"]
    )
    
    generator = QuestionGenerator()
    
    # Generate multiple questions
    q1 = generator.generate_next_question(job, [], question_number=1)
    q2 = generator.generate_next_question(job, [], question_number=2)
    q3 = generator.generate_next_question(job, [], question_number=3)
    
    # All should be valid questions
    assert all(isinstance(q, str) and len(q) > 0 for q in [q1, q2, q3])
    # Questions should be different (or at least valid)
    assert q1 != q2 or q2 != q3  # At least some variation


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
    
    generator = QuestionGenerator()
    
    q1 = generator.generate_initial_question(job1)
    q2 = generator.generate_initial_question(job2)
    
    # Questions should reflect different jobs
    assert "Product Manager" in q1 or "Product" in q1 or "Strategy" in q1
    assert "Data Scientist" in q2 or "Data" in q2 or "Python" in q2 or "ML" in q2

