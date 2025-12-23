"""Tests for Job model and data loading."""
import json
import pytest
from pathlib import Path
from models.job import Job, load_jobs


def test_job_dataclass_has_required_fields():
    """Test that Job dataclass has all required fields."""
    job = Job(
        id="job_1",
        title="Software Engineer",
        description="Build amazing software",
        department="Engineering",
        location="Remote",
        requirements=["Python", "FastAPI"]
    )
    
    assert job.id == "job_1"
    assert job.title == "Software Engineer"
    assert job.description == "Build amazing software"
    assert job.department == "Engineering"
    assert job.location == "Remote"
    assert job.requirements == ["Python", "FastAPI"]


def test_load_jobs_reads_json_file(tmp_path):
    """Test that load_jobs reads and parses JSON file correctly."""
    # Create temporary jobs.json file
    jobs_data = [
        {
            "id": "job_1",
            "title": "Software Engineer",
            "description": "Build amazing software",
            "department": "Engineering",
            "location": "Remote",
            "requirements": ["Python", "FastAPI"]
        },
        {
            "id": "job_2",
            "title": "Product Manager",
            "description": "Lead product development",
            "department": "Product",
            "location": "San Francisco",
            "requirements": ["Strategy", "Communication"]
        }
    ]
    
    jobs_file = tmp_path / "jobs.json"
    jobs_file.write_text(json.dumps(jobs_data))
    
    # Mock the path to use our temp file
    jobs = load_jobs(str(jobs_file))
    
    assert len(jobs) == 2
    assert jobs[0].id == "job_1"
    assert jobs[0].title == "Software Engineer"
    assert jobs[1].id == "job_2"
    assert jobs[1].title == "Product Manager"


def test_load_jobs_returns_list_of_job_objects(tmp_path):
    """Test that load_jobs returns list of Job instances."""
    jobs_data = [
        {
            "id": "job_1",
            "title": "Software Engineer",
            "description": "Build amazing software",
            "department": "Engineering",
            "location": "Remote",
            "requirements": ["Python"]
        }
    ]
    
    jobs_file = tmp_path / "jobs.json"
    jobs_file.write_text(json.dumps(jobs_data))
    
    jobs = load_jobs(str(jobs_file))
    
    assert isinstance(jobs, list)
    assert len(jobs) == 1
    assert isinstance(jobs[0], Job)


def test_load_jobs_handles_missing_file():
    """Test that load_jobs raises appropriate error for missing file."""
    with pytest.raises(FileNotFoundError):
        load_jobs("nonexistent_file.json")


def test_load_jobs_validates_required_fields(tmp_path):
    """Test that load_jobs validates all required fields are present."""
    # Missing 'requirements' field
    invalid_job = {
        "id": "job_1",
        "title": "Software Engineer",
        "description": "Build amazing software",
        "department": "Engineering",
        "location": "Remote"
    }
    
    jobs_file = tmp_path / "jobs.json"
    jobs_file.write_text(json.dumps([invalid_job]))
    
    with pytest.raises((KeyError, ValueError)):
        load_jobs(str(jobs_file))


def test_load_jobs_returns_at_least_3_jobs():
    """Test that load_jobs returns at least 3 jobs from data/jobs.json."""
    # This test uses the actual data file
    project_root = Path(__file__).parent.parent
    jobs_file = project_root / "data" / "jobs.json"
    
    if jobs_file.exists():
        jobs = load_jobs(str(jobs_file))
        assert len(jobs) >= 3
        assert all(isinstance(job, Job) for job in jobs)

