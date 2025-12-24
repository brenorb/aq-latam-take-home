"""Tests for session repository."""
import pytest
import sqlite3
import json
from datetime import datetime, timezone
import tempfile
import os

from backend.database.db import init_db
from backend.database.session_repository import SessionRepository
from backend.models.interview import InterviewState
from models.job import Job


def test_session_repository_save_session():
    """Test that SessionRepository can save a session."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    try:
        init_db(db_path)
        repo = SessionRepository(db_path)
        
        # Create mock interview state
        job = Job(
            id="job_1",
            title="Software Engineer",
            description="Build software",
            department="Engineering",
            location="Remote",
            requirements=["Python", "FastAPI"]
        )
        
        started_at = datetime.now(timezone.utc)
        ended_at = datetime.now(timezone.utc)
        
        interview_state: InterviewState = {
            "session_id": "test_session_123",
            "job_id": "job_1",
            "job": job,
            "conversation_history": [
                {
                    "question": "Why are you interested?",
                    "answer": "I love coding",
                    "question_number": 1,
                    "is_followup": False,
                }
            ],
            "current_question": None,
            "current_question_number": 1,
            "current_question_is_followup": False,
            "standalone_question_count": 1,
            "follow_up_count": 0,
            "total_question_count": 1,
            "started_at": started_at,
            "ended_at": ended_at,
            "is_complete": True,
        }
        
        repo.save_session("test_session_123", interview_state)
        
        # Verify session was saved
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE session_id = ?", ("test_session_123",))
        row = cursor.fetchone()
        
        assert row is not None
        assert row[0] == "test_session_123"  # session_id
        assert row[1] == "job_1"  # job_id
        assert row[2] == "Software Engineer"  # job_title
        assert row[3] == "Engineering"  # job_department
        
        # Verify conversation_history JSON
        history_json = json.loads(row[4])
        assert len(history_json) == 1
        assert history_json[0]["question"] == "Why are you interested?"
        assert history_json[0]["answer"] == "I love coding"
        
        conn.close()
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_session_repository_get_session():
    """Test that SessionRepository can retrieve a saved session."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    try:
        init_db(db_path)
        repo = SessionRepository(db_path)
        
        # Save a session first
        job = Job(
            id="job_1",
            title="Software Engineer",
            description="Build software",
            department="Engineering",
            location="Remote",
            requirements=["Python"]
        )
        
        started_at = datetime.now(timezone.utc)
        ended_at = datetime.now(timezone.utc)
        
        interview_state: InterviewState = {
            "session_id": "test_session_456",
            "job_id": "job_1",
            "job": job,
            "conversation_history": [
                {
                    "question": "Q1",
                    "answer": "A1",
                    "question_number": 1,
                    "is_followup": False,
                },
                {
                    "question": "Q2",
                    "answer": "A2",
                    "question_number": 2,
                    "is_followup": True,
                }
            ],
            "current_question": None,
            "current_question_number": 2,
            "current_question_is_followup": True,
            "standalone_question_count": 1,
            "follow_up_count": 1,
            "total_question_count": 2,
            "started_at": started_at,
            "ended_at": ended_at,
            "is_complete": True,
        }
        
        repo.save_session("test_session_456", interview_state)
        
        # Retrieve session
        session = repo.get_session("test_session_456")
        
        assert session is not None
        assert session["session_id"] == "test_session_456"
        assert session["job_id"] == "job_1"
        assert session["job_title"] == "Software Engineer"
        assert session["job_department"] == "Engineering"
        assert len(session["conversation_history"]) == 2
        assert session["conversation_history"][0]["question"] == "Q1"
        assert session["conversation_history"][1]["question"] == "Q2"
        assert session["ended_at"] is not None
        
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_session_repository_get_nonexistent_session():
    """Test that SessionRepository returns None for nonexistent session."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    try:
        init_db(db_path)
        repo = SessionRepository(db_path)
        
        session = repo.get_session("nonexistent_session")
        
        assert session is None
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_session_repository_get_all_sessions():
    """Test that SessionRepository can retrieve all sessions."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    try:
        init_db(db_path)
        repo = SessionRepository(db_path)
        
        job = Job(
            id="job_1",
            title="Software Engineer",
            description="Build software",
            department="Engineering",
            location="Remote",
            requirements=["Python"]
        )
        
        # Save multiple sessions
        for i in range(3):
            interview_state: InterviewState = {
                "session_id": f"session_{i}",
                "job_id": "job_1",
                "job": job,
                "conversation_history": [],
                "current_question": None,
                "current_question_number": 1,
                "current_question_is_followup": False,
                "standalone_question_count": 1,
                "follow_up_count": 0,
                "total_question_count": 1,
                "started_at": datetime.now(timezone.utc),
                "ended_at": datetime.now(timezone.utc),
                "is_complete": True,
            }
            repo.save_session(f"session_{i}", interview_state)
        
        sessions = repo.get_all_sessions()
        
        assert len(sessions) == 3
        session_ids = {s["session_id"] for s in sessions}
        assert session_ids == {"session_0", "session_1", "session_2"}
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_session_repository_save_session_preserves_created_at():
    """Test that saving a session twice preserves the original created_at timestamp."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    try:
        init_db(db_path)
        repo = SessionRepository(db_path)
        
        job = Job(
            id="job_1",
            title="Software Engineer",
            description="Build software",
            department="Engineering",
            location="Remote",
            requirements=["Python"]
        )
        
        started_at = datetime.now(timezone.utc)
        ended_at = datetime.now(timezone.utc)
        
        interview_state: InterviewState = {
            "session_id": "test_session_update",
            "job_id": "job_1",
            "job": job,
            "conversation_history": [
                {
                    "question": "Q1",
                    "answer": "A1",
                    "question_number": 1,
                    "is_followup": False,
                }
            ],
            "current_question": None,
            "current_question_number": 1,
            "current_question_is_followup": False,
            "standalone_question_count": 1,
            "follow_up_count": 0,
            "total_question_count": 1,
            "started_at": started_at,
            "ended_at": ended_at,
            "is_complete": True,
        }
        
        # Save session first time
        repo.save_session("test_session_update", interview_state)
        
        # Get original created_at
        session1 = repo.get_session("test_session_update")
        original_created_at = session1["created_at"]
        
        # Update conversation history
        interview_state["conversation_history"].append({
            "question": "Q2",
            "answer": "A2",
            "question_number": 2,
            "is_followup": True,
        })
        
        # Save session second time (should UPDATE, not INSERT)
        repo.save_session("test_session_update", interview_state)
        
        # Get updated session
        session2 = repo.get_session("test_session_update")
        updated_created_at = session2["created_at"]
        
        # Verify created_at is preserved
        assert updated_created_at == original_created_at
        
        # Verify conversation_history was updated
        assert len(session2["conversation_history"]) == 2
        assert session2["conversation_history"][1]["question"] == "Q2"
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)

