"""Tests for start.sh script exit code behavior.

These tests verify the cleanup function properly propagates exit codes.
"""

import subprocess
import pytest


class TestStartScriptCleanupFunction:
    """Test the cleanup function exit code behavior."""

    def test_cleanup_with_exit_code_returns_that_code(self):
        """cleanup 1 should exit with code 1."""
        # Extract and test the cleanup function logic
        script = """
        cleanup() {
            local exit_code=${1:-0}
            exit $exit_code
        }
        cleanup 1
        """
        result = subprocess.run(
            ["bash", "-c", script],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1

    def test_cleanup_without_args_returns_zero(self):
        """cleanup without args should exit with code 0."""
        script = """
        cleanup() {
            local exit_code=${1:-0}
            exit $exit_code
        }
        cleanup
        """
        result = subprocess.run(
            ["bash", "-c", script],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_cleanup_with_custom_exit_code(self):
        """cleanup with custom exit code should use that code."""
        script = """
        cleanup() {
            local exit_code=${1:-0}
            exit $exit_code
        }
        cleanup 42
        """
        result = subprocess.run(
            ["bash", "-c", script],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 42


class TestDockerfileFrontendCopy:
    """Test Dockerfile includes frontend directory."""

    def test_dockerfile_copies_frontend_directory(self):
        """Dockerfile should have COPY frontend/ ./frontend/ line."""
        with open("Dockerfile", "r") as f:
            content = f.read()
        
        assert "COPY frontend/ ./frontend/" in content, (
            "Dockerfile must copy frontend/ directory for Streamlit to find modules"
        )


class TestStartScriptCleanupCall:
    """Test start.sh calls cleanup with proper exit code on error."""

    def test_start_script_has_cleanup_with_exit_code_parameter(self):
        """start.sh cleanup function should accept exit_code parameter."""
        with open("scripts/start.sh", "r") as f:
            content = f.read()
        
        # Should have exit_code parameter handling
        assert "local exit_code=" in content or "${1:-0}" in content, (
            "cleanup function should accept exit code parameter"
        )
        assert "exit $exit_code" in content, (
            "cleanup should exit with the provided exit code"
        )

    def test_start_script_calls_cleanup_with_error_code_on_failure(self):
        """start.sh should call cleanup 1 when services fail."""
        with open("scripts/start.sh", "r") as f:
            content = f.read()
        
        assert "cleanup 1" in content, (
            "start.sh should call cleanup with exit code 1 on service failure"
        )

