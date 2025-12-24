"""Tests for backend configuration (environment variables, CORS, logging, error handling)."""
import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


def test_cors_configuration_from_env():
    """Test that CORS origins can be configured via environment variable."""
    with patch.dict(os.environ, {"CORS_ORIGINS": "https://app.example.com,https://staging.example.com"}):
        # Reload the app module to pick up new env vars
        import importlib
        from backend import main
        importlib.reload(main)
        
        client = TestClient(main.app)
        response = client.options("/api/interviews/start")
        
        # CORS middleware should be configured
        assert response.status_code in [200, 204, 405]


def test_cors_configuration_default():
    """Test that CORS defaults to localhost:8501 when not set."""
    # Remove CORS_ORIGINS if it exists
    env_backup = os.environ.pop("CORS_ORIGINS", None)
    try:
        import importlib
        from backend import main
        importlib.reload(main)
        
        client = TestClient(main.app)
        # Should work with default CORS config
        response = client.get("/health")
        assert response.status_code == 200
    finally:
        if env_backup:
            os.environ["CORS_ORIGINS"] = env_backup


def test_cors_configuration_wildcard():
    """Test that CORS can be configured to allow all origins."""
    with patch.dict(os.environ, {"CORS_ORIGINS": "*"}):
        import importlib
        from backend import main
        importlib.reload(main)
        
        client = TestClient(main.app)
        response = client.get("/health")
        assert response.status_code == 200


def test_log_level_configuration():
    """Test that log level can be configured via environment variable."""
    with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}):
        import importlib
        import logging
        from backend import main
        importlib.reload(main)
        
        # Logger should be configured
        logger = logging.getLogger("backend.main")
        assert logger.level <= logging.DEBUG


def test_log_level_default():
    """Test that log level defaults to INFO when not set."""
    env_backup = os.environ.pop("LOG_LEVEL", None)
    try:
        import importlib
        import logging
        from backend import main
        importlib.reload(main)
        
        logger = logging.getLogger("backend.main")
        # Default should be INFO or higher
        assert logger.level >= logging.INFO
    finally:
        if env_backup:
            os.environ["LOG_LEVEL"] = env_backup


def test_production_error_handling():
    """Test that production errors don't expose stack traces."""
    with patch.dict(os.environ, {"DEBUG_MODE": "false"}):
        import importlib
        from backend import main
        importlib.reload(main)
        
        client = TestClient(main.app)
        
        # Trigger an error (invalid endpoint or internal error)
        # We'll test with a route that might cause an error
        response = client.post("/api/interviews/start", json={"job_id": "invalid_job"})
        
        # Error response should not contain stack traces
        assert response.status_code in [400, 404, 500]
        data = response.json()
        error_str = str(data).lower()
        assert "traceback" not in error_str
        assert "file" not in error_str or "line" not in error_str.lower()


def test_health_endpoint():
    """Test that health check endpoint works."""
    from backend import main
    client = TestClient(main.app)
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_database_path_configuration():
    """Test that database path can be configured via environment variable."""
    import tempfile
    import os
    from pathlib import Path
    
    with tempfile.TemporaryDirectory() as tmpdir:
        custom_db_path = os.path.join(tmpdir, "custom_interviews.db")
        
        with patch.dict(os.environ, {"DATABASE_PATH": custom_db_path}):
            from backend.database import db
            import importlib
            importlib.reload(db)
            
            # Database path should be configurable
            db_path = db._get_db_path()
            assert db_path == custom_db_path


def test_database_path_default():
    """Test that database path defaults to data/interviews.db when not set."""
    env_backup = os.environ.pop("DATABASE_PATH", None)
    try:
        from backend.database import db
        import importlib
        importlib.reload(db)
        
        db_path = db._get_db_path()
        assert "data" in db_path
        assert "interviews.db" in db_path
    finally:
        if env_backup:
            os.environ["DATABASE_PATH"] = env_backup


def test_database_directory_creation():
    """Test that database directory is created if it doesn't exist."""
    import tempfile
    import os
    from pathlib import Path
    
    with tempfile.TemporaryDirectory() as tmpdir:
        custom_db_dir = os.path.join(tmpdir, "custom_data")
        custom_db_path = os.path.join(custom_db_dir, "interviews.db")
        
        # Directory shouldn't exist yet
        assert not os.path.exists(custom_db_dir)
        
        with patch.dict(os.environ, {"DATABASE_PATH": custom_db_path}):
            from backend.database import db
            import importlib
            importlib.reload(db)
            
            # Initialize database - should create directory
            db.init_db()
            
            # Directory should now exist
            assert os.path.exists(custom_db_dir)
            assert os.path.exists(custom_db_path)

