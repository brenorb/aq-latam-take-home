"""Database connection and initialization."""
import sqlite3
from pathlib import Path
from typing import Optional


def init_db(db_path: Optional[str] = None) -> None:
    """
    Initialize database and create tables if they don't exist.
    
    This function is kept for backward compatibility and explicit initialization.
    Tables are automatically created when get_db_connection() is called.
    
    Args:
        db_path: Path to database file. If None, uses default data/interviews.db
    """
    db_path = _get_db_path(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            job_id TEXT NOT NULL,
            job_title TEXT NOT NULL,
            job_department TEXT NOT NULL,
            conversation_history TEXT NOT NULL,
            started_at TEXT NOT NULL,
            ended_at TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()


def _get_db_path(db_path: Optional[str] = None) -> str:
    """
    Get database file path, creating directory if needed.
    
    Args:
        db_path: Path to database file. If None, uses default data/interviews.db
        
    Returns:
        Database file path as string
    """
    if db_path is None:
        project_root = Path(__file__).parent.parent.parent
        data_dir = project_root / "data"
        data_dir.mkdir(exist_ok=True)
        db_path = str(data_dir / "interviews.db")
    return db_path


def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """
    Get a database connection.
    
    Creates tables if they don't exist (idempotent operation).
    
    Args:
        db_path: Path to database file. If None, uses default data/interviews.db
        
    Returns:
        SQLite connection object
    """
    db_path = _get_db_path(db_path)
    
    # Connect and ensure tables exist in a single operation
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create sessions table if it doesn't exist (idempotent)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            job_id TEXT NOT NULL,
            job_title TEXT NOT NULL,
            job_department TEXT NOT NULL,
            conversation_history TEXT NOT NULL,
            started_at TEXT NOT NULL,
            ended_at TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    
    return conn

