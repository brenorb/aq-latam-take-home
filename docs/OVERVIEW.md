# AI Interviewer Platform - Overview

## Introduction

The AI Interviewer Platform is a lightweight web application that enables candidates to complete AI-driven voice interviews for specific job roles. The platform provides an interactive interview experience where an AI interviewer asks dynamic, context-aware questions that adapt based on candidate responses.

## Current Status

The platform provides a complete interview room interface with mock question generation and simulated conversation flow. Voice input and backend AI integration are planned for future implementation.

### Features

- **Job Listing Page**: Displays all available positions with full details (title, department, location, description, requirements)
- **Job Selection**: Users can click on any job to navigate to its interview room
- **Interview Room**: Complete UI with:
  - **Question Display**: Prominently styled question area that displays role-grounded mock questions
  - **Mock Question Generation**: Automatically generates 4 interview questions tailored to the selected job (title, department, requirements)
  - **Microphone Input Area**: Visual microphone button (UI only, no audio capture yet)
  - **Conversation History**: Scrollable panel displaying Q/A pairs in chronological order
  - **Interview Controls**: Start Interview, Submit Answer, and End Interview buttons
  - **State Management**: Per-job interview state tracking (conversation history, current question, interview status)
- **Navigation**: Seamless navigation between job listing and interview room pages using Streamlit session state

## Architecture

### Frontend
- **Framework**: Streamlit web application
- **State Management**: Streamlit session state for navigation (`current_page`, `selected_job_id`) and interview state (per-job: `interview_started`, `mock_conversation`, `current_mock_question`, `mock_questions`, `question_index`)
- **Structure**: Single-file application (`main.py`) with page rendering functions
- **Mock Question Generation**: `generate_mock_questions()` function creates role-grounded questions based on job details

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
   - Displays selected job information in collapsible expander
   - Two-column layout: question/answer area (70%) and conversation history (30%)
   - **Question Display**: Shows current interview question in a styled box with prominent visual distinction
   - **Answer Input**: Microphone button for voice input (visual only, non-functional)
   - **Conversation History**: Displays completed Q/A pairs in scrollable container
   - **Interview Flow**: 
     - Click "Start Interview" to begin and see first question
     - Click "Submit Answer" to simulate answering and advance to next question
     - Click "End Interview" to reset interview state
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

