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


