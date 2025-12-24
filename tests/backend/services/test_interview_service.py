"""Tests for dependency injection in InterviewService."""
import pytest
from unittest.mock import Mock, MagicMock, patch
from backend.services.interview_service import InterviewService
from backend.services.protocols import (
    IQuestionGenerator,
    ITTSProvider,
    ISTTProvider,
    IEvaluationProvider,
)
from models.job import Job, load_jobs


class MockQuestionGenerator:
    """Mock implementation of IQuestionGenerator for testing."""
    
    def __init__(self, job: Job = None):
        self.initial_question = "Mock initial question"
        self.next_questions = []  # List of (question, is_followup) tuples
        self.call_count = 0
        self.job = job
    
    def generate_question(self, input: str) -> tuple[str, bool]:
        self.call_count += 1
        if input == "":
            # Initial question
            return (self.initial_question, False)
        if self.next_questions:
            return self.next_questions.pop(0)
        return (f"Mock question {self.call_count}", False)


def test_interview_service_accepts_question_generator_injection():
    """Test that InterviewService accepts QuestionGenerator via dependency injection."""
    jobs = load_jobs()
    job = next(j for j in jobs if j.id == "job_1")
    
    def mock_generator_factory(job: Job):
        mock_gen = MockQuestionGenerator(job)
        mock_gen.initial_question = "Injected initial question"
        return mock_gen
    
    service = InterviewService(question_generator=mock_generator_factory)
    
    result = service.start_interview("job_1")
    
    assert result["question"] == "Injected initial question"
    # Get the generator instance that was created
    session_id = result["session_id"]
    generator = service._question_generators[session_id]
    assert generator.call_count == 1


def test_interview_service_uses_injected_generator_for_subsequent_questions():
    """Test that InterviewService uses injected generator for all questions."""
    # MockQuestionGenerator needs to be a factory/class, not an instance
    # Since it takes job in __init__, we'll pass it as a class
    jobs = load_jobs()
    job = next(j for j in jobs if j.id == "job_1")
    
    def mock_generator_factory(job: Job):
        mock_gen = MockQuestionGenerator(job)
        mock_gen.initial_question = "Question 1"
        mock_gen.next_questions = [("Question 2", False), ("Question 3", True)]
        return mock_gen
    
    service = InterviewService(question_generator=mock_generator_factory)
    
    start_result = service.start_interview("job_1")
    assert start_result["question"] == "Question 1"
    
    answer_result = service.submit_answer(start_result["session_id"], "Answer 1")
    assert answer_result["question"] == "Question 2"
    
    answer_result2 = service.submit_answer(start_result["session_id"], "Answer 2")
    assert answer_result2["question"] == "Question 3"


def test_interview_service_defaults_to_question_generator():
    """Test that InterviewService creates QuestionGenerator by default if not injected."""
    with patch("backend.services.interview_service.QuestionGenerator") as mock_generator_class:
        mock_generator = MagicMock()
        mock_generator.generate_question.return_value = ("Test question", False)
        mock_generator_class.return_value = mock_generator
        
        service = InterviewService()
        
        # Should work without explicit injection
        result = service.start_interview("job_1")
        
        assert "question" in result
        assert isinstance(result["question"], str)
        assert len(result["question"]) > 0


def test_interview_service_passes_job_to_generator():
    """Test that InterviewService passes job correctly to generator."""
    received_jobs = []
    
    def mock_generator_factory(job: Job):
        received_jobs.append(job)
        mock_gen = MockQuestionGenerator(job)
        mock_gen.generate_question = lambda input: ("Question", False)
        return mock_gen
    
    service = InterviewService(question_generator=mock_generator_factory)
    service.start_interview("job_1")
    
    assert len(received_jobs) == 1
    assert received_jobs[0].id == "job_1"


def test_interview_service_passes_answer_to_generator():
    """Test that InterviewService passes candidate answer to generator."""
    received_inputs = []
    
    def mock_generator_factory(job: Job):
        mock_gen = MockQuestionGenerator(job)
        
        def capture_input(input: str) -> tuple[str, bool]:
            received_inputs.append(input)
            return ("Next question", False)
        
        mock_gen.generate_question = capture_input
        return mock_gen
    
    service = InterviewService(question_generator=mock_generator_factory)
    start_result = service.start_interview("job_1")
    # First call should be with empty string for initial question
    assert received_inputs == [""]
    
    service.submit_answer(start_result["session_id"], "Answer 1")
    # Second call should be with the answer
    assert len(received_inputs) == 2
    assert received_inputs[1] == "Answer 1"


def test_question_generator_implements_protocol():
    """Test that QuestionGenerator implements IQuestionGenerator protocol."""
    with patch("backend.services.question_generator.dspy") as mock_dspy:
        mock_result = MagicMock()
        mock_result.question = "Test question"
        mock_result.is_followup = False
        
        mock_interviewer = MagicMock()
        mock_interviewer.return_value = mock_result
        mock_dspy.ChainOfThought.return_value = mock_interviewer
        mock_dspy.History.return_value = MagicMock()
        
        from backend.services.question_generator import QuestionGenerator
        
        job = Job(
            id="test",
            title="Test",
            description="Test",
            department="Test",
            location="Test",
            requirements=["Test"]
        )
        
        generator = QuestionGenerator(job)
        
        # Verify it has the required methods
        assert hasattr(generator, "generate_question")
        
        # Verify method is callable
        assert callable(generator.generate_question)
        
        # Verify method signature works
        question, is_followup = generator.generate_question("")
        assert isinstance(question, str)
        assert isinstance(is_followup, bool)


def test_interview_service_accepts_optional_tts_provider():
    """Test that InterviewService can accept optional TTS provider."""
    mock_tts = Mock(spec=ITTSProvider)
    mock_tts.synthesize.return_value = b"audio_data"
    
    service = InterviewService(tts_provider=mock_tts)
    
    # Service should be created successfully
    assert service is not None
    # TTS provider should be stored (if InterviewService supports it)
    # This test documents the expected interface even if not implemented yet


def test_interview_service_accepts_optional_stt_provider():
    """Test that InterviewService can accept optional STT provider."""
    mock_stt = Mock(spec=ISTTProvider)
    mock_stt.transcribe.return_value = "transcribed text"
    
    service = InterviewService(stt_provider=mock_stt)
    
    # Service should be created successfully
    assert service is not None
    # STT provider should be stored (if InterviewService supports it)
    # This test documents the expected interface even if not implemented yet


def test_interview_service_accepts_optional_evaluation_provider():
    """Test that InterviewService can accept optional evaluation provider."""
    mock_eval = Mock(spec=IEvaluationProvider)
    mock_eval.evaluate.return_value = {
        "strengths": ["Good"],
        "concerns": ["None"],
        "overall_score": 85
    }
    
    service = InterviewService(evaluation_provider=mock_eval)
    
    # Service should be created successfully
    assert service is not None
    # Evaluation provider should be stored (if InterviewService supports it)
    # This test documents the expected interface even if not implemented yet

