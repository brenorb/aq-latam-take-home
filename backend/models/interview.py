"""Interview state data models."""
from datetime import datetime, timezone
from typing import TypedDict
from models.job import Job


class ConversationEntry(TypedDict):
    """
    Conversation history entry representing a Q/A pair.
    
    Attributes:
        question: The question that was asked
        answer: The answer provided by the user
        question_number: The question number (1-indexed)
        is_followup: Whether this question was a follow-up to the previous answer
    """
    question: str
    answer: str
    question_number: int
    is_followup: bool


class InterviewState(TypedDict):
    """
    Interview state data model.
    
    Attributes:
        session_id: Unique session identifier
        job_id: Job identifier
        job: Job instance
        conversation_history: List of Q/A pairs, each with question, answer, question_number, is_followup
        current_question: Current question being asked (None if interview complete)
        current_question_number: Current question number (1-indexed)
        current_question_is_followup: Whether the current question is a follow-up
        standalone_question_count: Number of standalone (non-follow-up) questions asked
        follow_up_count: Number of follow-up questions asked
        total_question_count: Total questions asked (standalone + follow-up)
        started_at: Timestamp when interview started
        ended_at: Timestamp when interview ended (None if not ended)
        is_complete: Whether interview is complete
    """
    session_id: str
    job_id: str
    job: Job
    conversation_history: list[ConversationEntry]
    current_question: str | None
    current_question_number: int
    current_question_is_followup: bool
    standalone_question_count: int
    follow_up_count: int
    total_question_count: int
    started_at: datetime
    ended_at: datetime | None
    is_complete: bool

