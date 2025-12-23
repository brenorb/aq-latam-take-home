# AI Interviewer Platform - Overview

## Introduction

The AI Interviewer Platform is a lightweight web application that enables candidates to complete AI-driven voice interviews for specific job roles. The platform provides an interactive interview experience where an AI interviewer asks dynamic, context-aware questions that adapt based on candidate responses.

## Current Status

The platform provides a complete interview experience with a FastAPI backend handling interview orchestration and question generation. The frontend communicates with the backend via REST API endpoints. Questions are generated using template-based role-grounded logic. Voice input is planned for future implementation.

### Features

- **Job Listing Page**: Displays all available positions with full details (title, department, location, description, requirements)
- **Job Selection**: Users can click on any job to navigate to its interview room
- **Interview Room**: Complete UI with:
  - **Question Display**: Prominently styled question area that displays role-grounded questions from the backend
  - **Question Generation**: Backend generates interview questions tailored to the selected job (title, department, requirements)
  - **Text Input**: Text area for typing answers (voice input coming soon)
  - **Conversation History**: Scrollable panel displaying Q/A pairs in chronological order, synced with backend
  - **Interview Controls**: Start Interview, Submit Answer, and End Interview buttons
  - **Session Management**: Backend manages interview sessions with unique session IDs
- **REST API**: FastAPI backend provides endpoints for interview lifecycle management
- **Navigation**: Seamless navigation between job listing and interview room pages using Streamlit session state

## Architecture

### Frontend
- **Framework**: Streamlit web application
- **State Management**: Streamlit session state for navigation (`current_page`, `selected_job_id`) and interview state (session_id, current_question, conversation_history)
- **Structure**: Single-file application (`main.py`) with page rendering functions
- **API Client**: `api_client.py` handles HTTP communication with FastAPI backend using httpx

### Backend
- **Framework**: FastAPI REST API service
- **Entry Point**: `backend/main.py` - FastAPI application with CORS middleware
- **Routes**: `backend/api/routes.py` - API endpoints for interview operations
- **Schemas**: `backend/api/schemas.py` - Pydantic models for request/response validation
- **Services**:
  - `backend/services/interview_service.py` - Interview orchestration and session management
  - `backend/services/question_generator.py` - Template-based question generation
- **Models**: `backend/models/interview.py` - Interview state data structures

### API Endpoints

- `POST /api/interviews/start` - Initialize interview session with job role
- `POST /api/interviews/{session_id}/answer` - Submit user answer and get next question
- `POST /api/interviews/{session_id}/end` - Complete interview session
- `GET /health` - Health check endpoint

### Data Layer
- **Job Model**: `models/job.py` - Job dataclass with fields: id, title, description, department, location, requirements
- **Data Storage**: `data/jobs.json` - JSON file containing at least 3 sample jobs
- **Loading**: `load_jobs()` function reads JSON and returns list of Job instances
- **Session Storage**: In-memory dictionary keyed by session_id (will be replaced with database in future)

### Pages

1. **Job Listing Page** (`render_job_listing()`)
   - Displays all available jobs
   - Shows job details: title, department, location, description, requirements
   - Provides "Start Interview" button for each job

2. **Interview Room Page** (`render_interview_room()`)
   - Displays selected job information in collapsible expander
   - Two-column layout: question/answer area (70%) and conversation history (30%)
   - **Question Display**: Shows current interview question from backend API
   - **Answer Input**: Text area for typing answers (voice input coming soon)
   - **Conversation History**: Displays completed Q/A pairs synced from backend
   - **Interview Flow**: 
     - Click "Start Interview" to call API and begin session
     - Type answer and click "Submit Answer" to send to API and get next question
     - Click "End Interview" to complete session via API
   - Back button to return to job listings

## Running the Application

The application consists of two services that run separately:

### Backend (FastAPI)
```bash
uv run uvicorn backend.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### Frontend (Streamlit)
```bash
uv run streamlit run main.py
```

The frontend will start on `http://localhost:8501` by default.

**Note**: Both services must be running for the application to work. The frontend communicates with the backend API.

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

## API Usage

### Starting an Interview

```python
from api_client import start_interview

result = start_interview("job_1")
# Returns: {
#   "session_id": "uuid-string",
#   "question": "Why are you interested in this Software Engineer position?",
#   "question_number": 1,
#   "conversation_history": []
# }
```

### Submitting an Answer

```python
from api_client import submit_answer

result = submit_answer(session_id, "I am interested because...")
# Returns: {
#   "question": "Tell me about your experience with Python.",
#   "question_number": 2,
#   "interview_complete": false,
#   "conversation_history": [...]
# }
```

### Ending an Interview

```python
from api_client import end_interview

result = end_interview(session_id)
# Returns: {
#   "session_id": "uuid-string",
#   "message": "Interview ended successfully"
# }
```

## Configuration

The API base URL can be configured via environment variable:

```bash
export API_BASE_URL=http://localhost:8000
```

If not set, defaults to `http://localhost:8000`.

