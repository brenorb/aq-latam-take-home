"""Job model and data loading."""
from pathlib import Path
import json
from pydantic import BaseModel, ValidationError


class Job(BaseModel):
    """
    Job data model representing a position available for interview.
    
    Attributes:
        id: Unique identifier for the job (e.g., "job_1")
        title: Job title (e.g., "Software Engineer")
        description: Brief description of the role and responsibilities
        department: Department name (e.g., "Engineering")
        location: Job location (e.g., "Remote", "San Francisco")
        requirements: List of required skills or qualifications
    """
    id: str
    title: str
    description: str
    department: str
    location: str
    requirements: list[str]


def load_jobs(file_path: str | None = None) -> list[Job]:
    """
    Load jobs from JSON file with Pydantic validation.
    
    Args:
        file_path: Path to jobs.json file. If None, uses default data/jobs.json
        
    Returns:
        List of Job instances
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If JSON is invalid
        ValueError: If JSON structure is invalid (not an array) or validation fails
        ValidationError: If job data doesn't match the schema
    """
    if file_path is None:
        project_root = Path(__file__).parent.parent
        file_path = str(project_root / "data" / "jobs.json")
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Validate that root is a list/array
    if not isinstance(data, list):
        raise ValueError(f"Expected JSON array, got {type(data).__name__}")
    
    # Use Pydantic to validate and parse each job
    jobs = []
    for idx, job_data in enumerate(data):
        try:
            job = Job.model_validate(job_data)
            jobs.append(job)
        except ValidationError as e:
            job_id = job_data.get("id", f"index_{idx}")
            raise ValueError(f"Validation error for job {job_id}: {e}") from e
    
    return jobs

