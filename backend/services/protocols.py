"""Protocol interfaces for AI services to enable dependency inversion."""
from typing import Protocol

from models.job import Job


class IQuestionGenerator(Protocol):
    """Protocol for question generation services."""
    
    def generate_question(self, input: str) -> tuple[str, bool]:
        """
        Generate a question based on candidate's answer.
        
        Args:
            input: The candidate's answer to the previous question (empty string for initial question)
            
        Returns:
            Tuple of (question: str, is_followup: bool)
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

