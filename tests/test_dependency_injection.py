"""Tests for dependency injection in InterviewService."""
import pytest
from unittest.mock import Mock
from backend.services.interview_service import InterviewService
from backend.services.protocols import (
    IQuestionGenerator,
    ITTSProvider,
    ISTTProvider,
    IEvaluationProvider,
)
from models.job import Job


class MockQuestionGenerator:
    """Mock implementation of IQuestionGenerator for testing."""
    
    def __init__(self):
        self.initial_question = "Mock initial question"
        self.next_questions = []
        self.call_count = 0
    
    def generate_initial_question(self, job: Job) -> str:
        self.call_count += 1
        return self.initial_question
    
    def generate_next_question(
        self,
        job: Job,
        conversation_history: list[dict],
        question_number: int
    ) -> str:
        self.call_count += 1
        if self.next_questions:
            return self.next_questions.pop(0)
        return f"Mock question {question_number}"


def test_interview_service_accepts_question_generator_injection():
    """Test that InterviewService accepts QuestionGenerator via dependency injection."""
    mock_generator = MockQuestionGenerator()
    mock_generator.initial_question = "Injected initial question"
    
    service = InterviewService(question_generator=mock_generator)
    
    result = service.start_interview("job_1")
    
    assert result["question"] == "Injected initial question"
    assert mock_generator.call_count == 1


def test_interview_service_uses_injected_generator_for_subsequent_questions():
    """Test that InterviewService uses injected generator for all questions."""
    mock_generator = MockQuestionGenerator()
    mock_generator.initial_question = "Question 1"
    mock_generator.next_questions = ["Question 2", "Question 3"]
    
    service = InterviewService(question_generator=mock_generator)
    
    start_result = service.start_interview("job_1")
    assert start_result["question"] == "Question 1"
    
    answer_result = service.submit_answer(start_result["session_id"], "Answer 1")
    assert answer_result["question"] == "Question 2"
    
    answer_result2 = service.submit_answer(start_result["session_id"], "Answer 2")
    assert answer_result2["question"] == "Question 3"


def test_interview_service_defaults_to_question_generator():
    """Test that InterviewService creates QuestionGenerator by default if not injected."""
    service = InterviewService()
    
    # Should work without explicit injection
    result = service.start_interview("job_1")
    
    assert "question" in result
    assert isinstance(result["question"], str)
    assert len(result["question"]) > 0


def test_interview_service_passes_job_to_generator():
    """Test that InterviewService passes job correctly to generator."""
    mock_generator = MockQuestionGenerator()
    received_jobs = []
    
    def capture_job(job: Job) -> str:
        received_jobs.append(job)
        return "Question"
    
    mock_generator.generate_initial_question = capture_job
    
    service = InterviewService(question_generator=mock_generator)
    service.start_interview("job_1")
    
    assert len(received_jobs) == 1
    assert received_jobs[0].id == "job_1"


def test_interview_service_passes_conversation_history_to_generator():
    """Test that InterviewService passes conversation history to generator."""
    mock_generator = MockQuestionGenerator()
    received_histories = []
    
    def capture_history(job: Job, conversation_history: list[dict], question_number: int) -> str:
        received_histories.append((conversation_history.copy(), question_number))
        return "Next question"
    
    mock_generator.generate_next_question = capture_history
    
    service = InterviewService(question_generator=mock_generator)
    start_result = service.start_interview("job_1")
    service.submit_answer(start_result["session_id"], "Answer 1")
    
    assert len(received_histories) == 1
    history, q_num = received_histories[0]
    assert len(history) == 1
    assert history[0]["answer"] == "Answer 1"
    assert q_num == 2


def test_question_generator_implements_protocol():
    """Test that QuestionGenerator implements IQuestionGenerator protocol."""
    from backend.services.question_generator import QuestionGenerator
    
    generator = QuestionGenerator()
    
    # Verify it has the required methods
    assert hasattr(generator, "generate_initial_question")
    assert hasattr(generator, "generate_next_question")
    
    # Verify methods are callable
    assert callable(generator.generate_initial_question)
    assert callable(generator.generate_next_question)
    
    # Verify method signatures work
    job = Job(
        id="test",
        title="Test",
        description="Test",
        department="Test",
        location="Test",
        requirements=["Test"]
    )
    
    question = generator.generate_initial_question(job)
    assert isinstance(question, str)
    
    next_question = generator.generate_next_question(job, [], 1)
    assert isinstance(next_question, str)


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

