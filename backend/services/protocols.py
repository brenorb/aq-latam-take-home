"""Protocol interfaces for AI services to enable dependency inversion."""
from typing import Protocol
from models.job import Job


class IQuestionGenerator(Protocol):
    """Protocol for question generation services."""
    
    def generate_initial_question(self, job: Job) -> str:
        """
        Generate the first question for an interview.
        
        Args:
            job: The job instance to generate question for
            
        Returns:
            Role-grounded interview question string
        """
        ...
    
    def generate_next_question(
        self,
        job: Job,
        conversation_history: list[dict],
        question_number: int
    ) -> str:
        """
        Generate the next question based on conversation history.
        
        Args:
            job: The job instance to generate question for
            conversation_history: List of previous Q/A pairs
            question_number: Current question number (1-indexed)
            
        Returns:
            Role-grounded interview question string
        """
        ...


class ITTSProvider(Protocol):
    """Protocol for text-to-speech services."""
    
    def synthesize(self, text: str) -> bytes:
        """
        Convert text to speech audio.
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Audio data as bytes (format depends on implementation)
        """
        ...


class ISTTProvider(Protocol):
    """Protocol for speech-to-text services."""
    
    def transcribe(self, audio_data: bytes) -> str:
        """
        Convert speech audio to text.
        
        Args:
            audio_data: Audio data as bytes (format depends on implementation)
            
        Returns:
            Transcribed text string
        """
        ...


class IEvaluationProvider(Protocol):
    """Protocol for interview evaluation services."""
    
    def evaluate(
        self,
        job: Job,
        conversation_history: list[dict]
    ) -> dict:
        """
        Generate structured evaluation of interview.
        
        Args:
            job: The job instance that was interviewed for
            conversation_history: List of Q/A pairs from the interview
            
        Returns:
            Dictionary with evaluation containing:
            - strengths: list[str]
            - concerns: list[str]
            - overall_score: float or int
        """
        ...

