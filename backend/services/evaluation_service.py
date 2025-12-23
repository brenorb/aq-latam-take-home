"""AI-powered evaluation generation service."""
import logging

import dspy
from dspy.signatures.signature import make_signature

# Import DSPy configuration (sets up LM)
from backend.services import dspy_signature  # noqa: F401
from models.job import Job

# Evaluation signature for DSPy
evaluation_sig = {
    "job_context": (str, dspy.InputField()),
    "conversation_history": (str, dspy.InputField()),
    
    "strengths": (list[str], dspy.OutputField(desc="List of candidate strengths identified from the interview")),
    "concerns": (list[str], dspy.OutputField(desc="List of concerns or areas for improvement")),
    "overall_score": (float, dspy.OutputField(desc="Overall score from 0.0 to 100.0")),
}


class EvaluationService:
    """
    AI-powered evaluation generation service.
    
    Uses DSPy with LLM to analyze interview conversations and generate
    structured evaluations with strengths, concerns, and overall score.
    """
    
    def __init__(self):
        """Initialize evaluation service with DSPy module."""
        instructions = """You are an expert interviewer evaluating a candidate's interview performance.

Your task is to analyze the interview conversation and provide a structured evaluation.

Guidelines:
- Identify specific strengths demonstrated by the candidate
- Identify specific concerns or areas for improvement
- Provide an overall score from 0.0 to 100.0 based on:
  - Technical competence
  - Communication skills
  - Cultural fit
  - Overall performance
- Be specific and constructive in your feedback
- Base your evaluation solely on the conversation provided"""

        self._evaluator = dspy.ChainOfThought(make_signature(evaluation_sig, instructions))
    
    def evaluate(self, job: Job, conversation_history: list[dict]) -> dict:
        """
        Generate structured evaluation of interview.
        
        Args:
            job: The job instance that was interviewed for
            conversation_history: List of Q/A pairs from the interview
            
        Returns:
            Dictionary with evaluation containing:
            - strengths: list[str]
            - concerns: list[str]
            - overall_score: float (0.0 to 100.0)
        """
        # Build job context string
        job_context = f"""Job Title: {job.title}
Department: {job.department}
Description: {job.description}
Requirements: {', '.join(job.requirements) if job.requirements else 'None specified'}"""

        # Serialize conversation history to string
        conversation_text = "\n\n".join([
            f"Q{entry['question_number']} ({'Follow-up' if entry.get('is_followup') else 'Standalone'}): {entry['question']}\n"
            f"A: {entry['answer']}"
            for entry in conversation_history
        ])
        
        # Generate evaluation using DSPy with error handling
        try:
            response = self._evaluator(
                job_context=job_context,
                conversation_history=conversation_text
            )
        except Exception as e:
            # Log error and return default evaluation
            logging.error(f"Error generating evaluation: {e}", exc_info=True)
            return {
                "strengths": [],
                "concerns": ["Unable to generate evaluation due to technical error"],
                "overall_score": 0.0,
            }
                
        return {
            "strengths": response.strengths,
            "concerns": response.concerns,
            "overall_score": response.overall_score,
        }