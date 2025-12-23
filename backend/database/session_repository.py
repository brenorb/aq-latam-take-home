"""Session repository for database persistence."""
import json
import sqlite3
from datetime import datetime
from typing import Optional

from backend.database.db import get_db_connection
from backend.models.interview import InterviewState


class SessionRepository:
    """Repository for persisting and retrieving interview sessions."""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize session repository.
        
        Args:
            db_path: Path to database file. If None, uses default data/interviews.db
        """
        self.db_path = db_path
    
    def save_session(self, session_id: str, interview_state: InterviewState) -> None:
        """
        Save interview session to database.
        
        Args:
            session_id: Session identifier
            interview_state: InterviewState to save
            
        Raises:
            sqlite3.Error: If database operation fails
        """
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Serialize conversation_history to JSON
            conversation_json = json.dumps(interview_state["conversation_history"])
            
            # Convert datetime objects to ISO format strings
            started_at_iso = interview_state["started_at"].isoformat()
            ended_at_iso = (
                interview_state["ended_at"].isoformat()
                if interview_state["ended_at"] is not None
                else None
            )
            
            # Extract job information
            job = interview_state["job"]
            job_id = interview_state["job_id"]
            job_title = job.title
            job_department = job.department
            
            # Check if session already exists
            cursor.execute("SELECT session_id FROM sessions WHERE session_id = ?", (session_id,))
            exists = cursor.fetchone() is not None
            
            if exists:
                # Update existing session (preserves created_at)
                cursor.execute("""
                    UPDATE sessions SET
                        job_id = ?,
                        job_title = ?,
                        job_department = ?,
                        conversation_history = ?,
                        started_at = ?,
                        ended_at = ?
                    WHERE session_id = ?
                """, (
                    job_id,
                    job_title,
                    job_department,
                    conversation_json,
                    started_at_iso,
                    ended_at_iso,
                    session_id,
                ))
            else:
                # Insert new session record
                cursor.execute("""
                    INSERT INTO sessions (
                        session_id, job_id, job_title, job_department,
                        conversation_history, started_at, ended_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    job_id,
                    job_title,
                    job_department,
                    conversation_json,
                    started_at_iso,
                    ended_at_iso,
                ))
            
            conn.commit()
        finally:
            conn.close()
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """
        Retrieve session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with session data, or None if not found
        """
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT session_id, job_id, job_title, job_department,
                       conversation_history, started_at, ended_at, created_at
                FROM sessions
                WHERE session_id = ?
            """, (session_id,))
            
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            # Deserialize conversation_history from JSON
            conversation_history = json.loads(row[4])
            
            return {
                "session_id": row[0],
                "job_id": row[1],
                "job_title": row[2],
                "job_department": row[3],
                "conversation_history": conversation_history,
                "started_at": row[5],
                "ended_at": row[6],
                "created_at": row[7],
            }
        finally:
            conn.close()
    
    def get_all_sessions(self) -> list[dict]:
        """
        Retrieve all sessions.
        
        Returns:
            List of dictionaries with session data
        """
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT session_id, job_id, job_title, job_department,
                       conversation_history, started_at, ended_at, created_at
                FROM sessions
                ORDER BY created_at DESC
            """)
            
            rows = cursor.fetchall()
            
            sessions = []
            for row in rows:
                conversation_history = json.loads(row[4])
                sessions.append({
                    "session_id": row[0],
                    "job_id": row[1],
                    "job_title": row[2],
                    "job_department": row[3],
                    "conversation_history": conversation_history,
                    "started_at": row[5],
                    "ended_at": row[6],
                    "created_at": row[7],
                })
            
            return sessions
        finally:
            conn.close()

