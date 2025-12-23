"""Database models for session persistence."""
from typing import TypedDict


class SessionRecord(TypedDict):
    """
    Database record representing a saved interview session.
    
    Attributes:
        session_id: Unique session identifier (primary key)
        job_id: Job identifier
        job_title: Job title (denormalized)
        job_department: Job department (denormalized)
        conversation_history: JSON string of conversation entries
        started_at: ISO format datetime string when interview started
        ended_at: ISO format datetime string when interview ended (nullable)
        created_at: ISO format datetime string when record was created
    """
    session_id: str
    job_id: str
    job_title: str
    job_department: str
    conversation_history: str  # JSON string
    started_at: str  # ISO datetime string
    ended_at: str | None  # ISO datetime string, nullable
    created_at: str  # ISO datetime string

