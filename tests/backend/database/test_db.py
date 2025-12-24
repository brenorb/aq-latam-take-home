"""Tests for database initialization and connection."""
import pytest
import sqlite3
import os
import tempfile

from backend.database.db import init_db, get_db_connection


def test_init_db_creates_tables():
    """Test that database initialization creates sessions table."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    try:
        init_db(db_path)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check that sessions table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='sessions'
        """)
        result = cursor.fetchone()
        assert result is not None
        
        # Check table schema
        cursor.execute("PRAGMA table_info(sessions)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        assert "session_id" in columns
        assert "job_id" in columns
        assert "job_title" in columns
        assert "job_department" in columns
        assert "conversation_history" in columns
        assert "started_at" in columns
        assert "ended_at" in columns
        assert "created_at" in columns
        
        conn.close()
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_get_db_connection():
    """Test that get_db_connection returns a valid connection."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    try:
        init_db(db_path)
        conn = get_db_connection(db_path)
        
        assert conn is not None
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result == (1,)
        
        conn.close()
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)

