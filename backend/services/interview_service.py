"""Interview orchestration service."""
import uuid
from datetime import datetime, timezone
from backend.models.interview import InterviewState
from backend.services.question_generator import QuestionGenerator
from models.job import Job, load_jobs


class InterviewService:
    """
    Service for managing interview sessions.
    
    Handles interview lifecycle: starting, submitting answers, ending.
    Stores interview state in-memory (will be replaced with database in Phase 5).
    """
    
    def __init__(self, max_questions: int = 6):
        """
        Initialize interview service.
        
        Args:
            max_questions: Maximum number of questions before interview completes (default 6)
        """
        self._interviews: dict[str, InterviewState] = {}
        self._question_generator = QuestionGenerator()
        self.max_questions = max_questions
    
    def start_interview(self, job_id: str) -> dict:
        """
        Start a new interview session.
        
        Args:
            job_id: ID of the job to interview for
            
        Returns:
            Dictionary with session_id, question, question_number
            
        Raises:
            ValueError: If job_id is not found
        """
        # Load jobs and find the requested job
        jobs = load_jobs()
        job = next((j for j in jobs if j.id == job_id), None)
        
        if job is None:
            raise ValueError(f"Job with id '{job_id}' not found")
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Generate first question
        question = self._question_generator.generate_initial_question(job)
        
        # Create interview state
        interview_state: InterviewState = {
            "session_id": session_id,
            "job_id": job_id,
            "job": job,
            "conversation_history": [],
            "current_question": question,
            "current_question_number": 1,
            "started_at": datetime.now(timezone.utc),
            "ended_at": None,
            "is_complete": False,
        }
        
        # Store state
        self._interviews[session_id] = interview_state
        
        return {
            "session_id": session_id,
            "question": question,
            "question_number": 1,
            "conversation_history": [],
        }
    
    def submit_answer(self, session_id: str, answer: str) -> dict:
        """
        Submit an answer and get the next question.
        
        Args:
            session_id: Session identifier
            answer: User's answer text
            
        Returns:
            Dictionary with question, question_number, interview_complete
            
        Raises:
            ValueError: If session_id is invalid or answer is empty
        """
        if not answer or not answer.strip():
            raise ValueError("Answer cannot be empty")
        
        # Retrieve interview state
        if session_id not in self._interviews:
            raise ValueError(f"Session not found: {session_id}")
        
        state = self._interviews[session_id]
        
        if state["is_complete"]:
            raise ValueError("Interview is already complete")
        
        # Store the question number that was just answered (before incrementing)
        last_answered_question_number = state["current_question_number"]
        
        # Add current Q/A pair to conversation history
        state["conversation_history"].append({
            "question": state["current_question"],
            "answer": answer.strip(),
            "question_number": last_answered_question_number,
        })
        
        # Increment question number
        next_question_number = state["current_question_number"] + 1
        
        # Check if interview should continue
        if next_question_number > self.max_questions:
            # Interview complete
            state["is_complete"] = True
            state["ended_at"] = datetime.now(timezone.utc)
            state["current_question"] = None
            
            return {
                "question": None,
                "question_number": last_answered_question_number,
                "interview_complete": True,
                "conversation_history": state["conversation_history"],
            }
        
        # Generate next question
        next_question = self._question_generator.generate_next_question(
            state["job"],
            state["conversation_history"],
            next_question_number
        )
        
        # Update state
        state["current_question"] = next_question
        state["current_question_number"] = next_question_number
        
        return {
            "question": next_question,
            "question_number": next_question_number,
            "interview_complete": False,
            "conversation_history": state["conversation_history"],
        }
    
    def end_interview(self, session_id: str) -> dict:
        """
        End an interview session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with session_id and message
            
        Raises:
            ValueError: If session_id is invalid
        """
        if session_id not in self._interviews:
            raise ValueError(f"Session not found: {session_id}")
        
        state = self._interviews[session_id]
        
        # Mark as complete
        state["is_complete"] = True
        state["ended_at"] = datetime.now(timezone.utc)
        
        return {
            "session_id": session_id,
            "message": "Interview ended successfully",
        }

