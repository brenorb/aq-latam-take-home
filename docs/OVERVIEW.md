# AI Interviewer Platform - Overview

## Introduction

The AI Interviewer Platform is a lightweight web application that enables candidates to complete AI-driven voice interviews for specific job roles. The platform provides an interactive interview experience where an AI interviewer asks dynamic, context-aware questions that adapt based on candidate responses.

## Current Status: Phase 1 Complete

Phase 1 establishes the foundation of the platform with a working Streamlit web application that displays job listings and enables navigation to interview rooms.

### Phase 1 Features

- **Job Listing Page**: Displays all available positions with full details (title, department, location, description, requirements)
- **Job Selection**: Users can click on any job to navigate to its interview room
- **Interview Room Layout**: Basic page structure with placeholder sections for:
  - Question display area
  - Answer input area
  - Conversation history panel
  - End interview button (placeholder)
- **Navigation**: Seamless navigation between job listing and interview room pages using Streamlit session state

## Architecture

### Frontend
- **Framework**: Streamlit web application
- **State Management**: Streamlit session state (`current_page`, `selected_job_id`)
- **Structure**: Single-file application (`main.py`) with page rendering functions

### Data Layer
- **Job Model**: `models/job.py` - Job dataclass with fields: id, title, description, department, location, requirements
- **Data Storage**: `data/jobs.json` - JSON file containing at least 3 sample jobs
- **Loading**: `load_jobs()` function reads JSON and returns list of Job instances

### Pages

1. **Job Listing Page** (`render_job_listing()`)
   - Displays all available jobs
   - Shows job details: title, department, location, description, requirements
   - Provides "Start Interview" button for each job

2. **Interview Room Page** (`render_interview_room()`)
   - Displays selected job information
   - Layout structure with placeholder sections for future interview functionality
   - Back button to return to job listings

## Running the Application

```bash
uv run streamlit run main.py
```

The application will start on `http://localhost:8501` by default.

## Data Format

Jobs are stored in `data/jobs.json` with the following structure:

```json
[
  {
    "id": "job_1",
    "title": "Software Engineer",
    "description": "Build scalable web applications...",
    "department": "Engineering",
    "location": "Remote",
    "requirements": ["Python", "FastAPI", "PostgreSQL"]
  }
]
```

