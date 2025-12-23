"""Interview orchestration service."""
import uuid
from datetime import datetime, timezone
from typing import Optional

from backend.models.interview import InterviewState
from backend.services.protocols import (
    IEvaluationProvider,
    IQuestionGenerator,
    ISTTProvider,
    ITTSProvider,
)
from backend.services.question_generator import QuestionGenerator
from models.job import load_jobs


class InterviewService:
    """
    Service for managing interview sessions.
    
    Handles interview lifecycle: starting, submitting answers, ending.
    Stores interview state in-memory (database persistence planned for future).
    """
    
    def __init__(
        self,
        max_questions: int = 6,
        question_generator: Optional[IQuestionGenerator] = None,
        tts_provider: Optional[ITTSProvider] = None,
        stt_provider: Optional[ISTTProvider] = None,
        evaluation_provider: Optional[IEvaluationProvider] = None,
    ):
        """
        Initialize interview service.
        
        Args:
            max_questions: Maximum number of questions before interview completes (default 6)
            question_generator: Question generator service (defaults to QuestionGenerator)
            tts_provider: Text-to-speech provider (optional, for future use)
            stt_provider: Speech-to-text provider (optional, for future use)
            evaluation_provider: Evaluation provider (optional, for future use)
        """
        self._interviews: dict[str, InterviewState] = {}
        self._question_generators: dict[str, IQuestionGenerator] = {}  # One per interview session
        # If question_generator is provided, use it as a factory/class (callable) or instance
        # If it's callable, we'll instantiate it per interview with the job
        # If it's an instance, we'll use it directly (not ideal for multiple interviews)
        self._question_generator_factory = question_generator
        self._tts_provider = tts_provider
        self._stt_provider = stt_provider
        self._evaluation_provider = evaluation_provider
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
        
        # Create question generator for this interview session
        # QuestionGenerator maintains state (history), so we need one per session
        if self._question_generator_factory:
            # If it's callable, treat it as a factory/class and instantiate with job
            # Otherwise, use it as-is (assumes it's an instance that doesn't need job)
            if callable(self._question_generator_factory):
                generator = self._question_generator_factory(job)
            else:
                generator = self._question_generator_factory
        else:
            generator = QuestionGenerator(job)
        
        self._question_generators[session_id] = generator
        
        # Generate first question (always standalone) - use empty string for initial question
        question, is_followup = generator.generate_question("")
        
        # Create interview state
        interview_state: InterviewState = {
            "session_id": session_id,
            "job_id": job_id,
            "job": job,
            "conversation_history": [],
            "current_question": question,
            "current_question_number": 1,
            "current_question_is_followup": is_followup,  # Should be False for initial question
            "standalone_question_count": 1 if not is_followup else 0,
            "follow_up_count": 1 if is_followup else 0,
            "total_question_count": 1,
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
        
        # Get is_followup from the current question (stored when it was generated)
        current_question_is_followup = state.get("current_question_is_followup", False)
        
        # Add current Q/A pair to conversation history with is_followup from current question
        state["conversation_history"].append({
            "question": state["current_question"],
            "answer": answer.strip(),
            "question_number": last_answered_question_number,
            "is_followup": current_question_is_followup,
        })
        
        # Check completion criteria BEFORE generating next question
        # Completion criteria:
        # - Interview completes when: total_question_count >= 10 AND minimums are met
        # - Minimums met: standalone_question_count >= 6 AND follow_up_count >= 2
        # - Soft limit: total_question_count >= 10
        minimums_met = (
            state["standalone_question_count"] >= 6 and 
            state["follow_up_count"] >= 2
        )
        soft_limit_reached = state["total_question_count"] >= 10
        
        # Interview completes when soft limit reached AND minimums are met
        if soft_limit_reached and minimums_met:
            # Interview complete - don't generate next question
            state["is_complete"] = True
            state["ended_at"] = datetime.now(timezone.utc)
            state["current_question"] = None
            
            return {
                "question": None,
                "question_number": last_answered_question_number,
                "interview_complete": True,
                "conversation_history": state["conversation_history"],
            }
        
        # Increment question number
        next_question_number = state["current_question_number"] + 1
        
        # Get the question generator for this session
        generator = self._question_generators.get(session_id)
        if generator is None:
            # Fallback: create a new generator (shouldn't happen in normal flow)
            generator = QuestionGenerator(state["job"])
            self._question_generators[session_id] = generator
        
        # Generate next question (returns tuple: question, is_followup)
        # Use the candidate's answer as input
        next_question, is_followup = generator.generate_question(answer.strip())
        
        # Update counters based on question type
        if is_followup:
            state["follow_up_count"] += 1
        else:
            state["standalone_question_count"] += 1
        state["total_question_count"] += 1
        
        # Check completion again after generating new question
        # (in case the new question pushed us over limits)
        minimums_met_after = (
            state["standalone_question_count"] >= 6 and 
            state["follow_up_count"] >= 2
        )
        soft_limit_reached_after = state["total_question_count"] >= 10
        
        if soft_limit_reached_after and minimums_met_after:
            # Interview complete after generating this question
            state["is_complete"] = True
            state["ended_at"] = datetime.now(timezone.utc)
            state["current_question"] = None
            
            return {
                "question": None,
                "question_number": last_answered_question_number,
                "interview_complete": True,
                "conversation_history": state["conversation_history"],
            }
        
        # Update state with new question and its is_followup flag
        state["current_question"] = next_question
        state["current_question_number"] = next_question_number
        state["current_question_is_followup"] = is_followup
        
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

