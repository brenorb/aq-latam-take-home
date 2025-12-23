"""Question generation logic using DSPy."""
import dspy
from dspy.signatures.signature import make_signature

from backend.services.dspy_signature import io_sig
from models.job import Job


class QuestionGenerator(dspy.Module):
    """
    Generates role-grounded interview questions using DSPy.
    
    Questions are generated based on job context and conversation history.
    Uses DSPy with OpenRouter LLM provider for AI-driven question generation.
    """
    
    def __init__(self, job: Job):
        """Initialize question generator with DSPy module."""
        job_instructions = f"""You are an interviewer conducting a job interview for the position of {job.title} in the {job.department} department.

Job Description: {job.description}

Job Requirements: {', '.join(job.requirements) if job.requirements else 'None specified'}

Interview Requirements:
- You must ask at least 6 standalone questions (exploring new aspects of the role)
- You must ask at least 2 follow-up questions (seeking more information about previous answers)
- Try to stick to 10 questions total

Guidelines:
- Standalone questions should explore different aspects of the role, skills, experience, or fit
- Follow-up questions should seek more information about the candidate's previous answer
- Questions must be role-grounded and relevant to {job.title} position
- Avoid repeating questions already asked
- Make questions conversational and natural"""

        self.interviewer = dspy.ChainOfThought(make_signature(io_sig, job_instructions))
        self.history = dspy.History(messages=[])

    
    def forward(self, input: str) -> tuple[str, bool]:
        """
        DSPy Module forward method - required for DSPy optimization.
        
        This method is called by DSPy's optimization framework (e.g., MIPRO, BootstrapFewShot)
        when optimizing the module. It should not be called directly by application code.
        
        Args:
            input: The candidate's answer to the previous question (empty string for initial question)
            
        Returns:
            Tuple of (question: str, is_followup: bool)
        """
        response = self.interviewer(history=self.history, candidate_answer=input)
        
        # Update history with the Q/A pair for context in future questions
        # DSPy History messages is a list that we can append to
        if input:  # Only add non-empty answers (skip initial empty string)
            self.history.messages.append({
                "candidate_answer": input,
                "question": response.question,
                "is_followup": response.is_followup,
            })

        return (response.question, response.is_followup)

    def generate_question(self, input: str) -> tuple[str, bool]:
        """
        Public interface for question generation - required for dependency inversion.
        
        This method implements the IQuestionGenerator protocol and is used by InterviewService.
        It delegates to forward() which contains the actual DSPy logic.
        
        Args:
            input: The candidate's answer to the previous question (empty string for initial question)
            
        Returns:
            Tuple of (question: str, is_followup: bool)
        """
        return self.forward(input=input)