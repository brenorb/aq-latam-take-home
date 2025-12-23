# Technical Roadmap: AI Interviewer Platform

## Context

This roadmap breaks down the AI Interviewer Platform into sequential phases. Each phase delivers a complete, runnable increment that builds toward the final product: a lightweight web application where users select a job and complete an AI-driven voice interview with dynamic questions that adapt based on responses.

The application must support:
- Viewing a list of sample jobs (at least 3) with title and description
- Entering an Interview Room for a selected role
- Voice input via microphone
- AI interviewer asking at least 6 questions, including at least 2 follow-ups that depend on prior answers
- Role-grounded questions that reflect the selected job
- Session saving and display of full transcript (Q/A turns) and structured evaluation (JSON: strengths, concerns, overall score)
- Clean, functional UI with minimal friction
- End-to-end functionality in a hosted environment

---

## Phase 1: Basic Web Application with Job Listing

**Goal**: Establish a working web application that displays a list of jobs.

**Deliverable**: User can launch the app, see a list of at least 3 sample jobs (each with title and short description), and click on a job to navigate to its interview room (even if the room is not yet functional).

**Components**:
- Streamlit frontend application entry point
- Job data structure/model (hardcoded sample jobs for now)
- Job listing page/component
- Basic navigation/routing to interview room page

**Architectural Decisions**:
- Use Streamlit session state for navigation and job selection
- Define job schema early (id, title, description fields)
- Establish page structure pattern (job list page → interview room page)

**Dependencies**: None (starting from scratch)

---

## Phase 2: Interview Room UI Layout

**Goal**: Create the visual interface for the interview room.

**Deliverable**: User can enter an interview room and see the complete UI layout including: microphone input area, AI question display area, conversation history area, and end interview button. The UI is visually complete but not yet functional.

**Components**:
- Interview room page component
- UI layout components (question display, answer input area, conversation history panel)
- Basic styling for clean, minimal friction interface
- Placeholder states for when interview hasn't started

**Architectural Decisions**:
- Establish UI component structure for interview flow
- Define visual hierarchy for question/answer display
- Set up Streamlit components for voice input (UI only, not yet capturing audio)

**Dependencies**: Phase 1 (job selection and navigation)

---

## Phase 3: Voice Input Capture and Transcription

**Goal**: Enable users to speak via microphone and see their transcribed speech.

**Deliverable**: User can click a microphone button, speak, and see their transcribed text displayed in the UI. Transcription works end-to-end from microphone to text display.

**Components**:
- Microphone input capture component (using Streamlit audio recorder or browser audio API)
- Audio-to-text transcription service/integration (e.g., Whisper API, browser SpeechRecognition API, or similar)
- Transcription display component
- Error handling for microphone permissions and transcription failures

**Architectural Decisions**:
- Choose transcription approach (client-side browser API vs server-side service)
- Define audio format and quality requirements
- Establish error handling patterns for audio capture

**Dependencies**: Phase 2 (interview room UI exists)

---

## Phase 4: Backend API and Basic AI Question Generation

**Goal**: Create backend service that can generate interview questions based on job role.

**Deliverable**: Backend API endpoint accepts job role information and returns an initial interview question. Frontend can call this endpoint and display the question. Questions are role-grounded (reflect the selected job).

**Components**:
- FastAPI backend application
- Job role data structure/model
- AI question generation endpoint (using DSPy or LLM integration)
- Question generation logic that takes job role into account
- Frontend API client/calling code
- Basic error handling

**Architectural Decisions**:
- Establish FastAPI as backend framework
- Define API contract (request/response schemas)
- Choose AI/LLM provider and integration approach (DSPy setup)
- Set up communication pattern between Streamlit frontend and FastAPI backend

**Dependencies**: Phase 3 (voice input exists, can now send transcribed text to backend)

---

## Phase 5: Full Interview Flow with Dynamic Questions

**Goal**: Implement complete interview conversation where AI asks questions, user responds, and AI generates follow-up questions based on responses.

**Deliverable**: User can complete a full interview session where:
- AI asks at least 6 questions total
- At least 2 questions are follow-ups that depend on the user's prior answer
- Questions are role-grounded
- Conversation flows naturally with Q/A turns displayed in real-time
- User can end the interview when complete

**Components**:
- Interview state management (tracking question count, conversation history, current question)
- Question generation logic that analyzes previous answers to generate follow-ups
- Conversation flow orchestration (when to ask follow-up vs new question)
- Frontend conversation display (showing Q/A turns in real-time)
- Interview completion logic

**Architectural Decisions**:
- Define interview state schema (question number, question type, answer history)
- Establish follow-up question generation strategy (analyze answer content, detect gaps, generate targeted follow-ups)
- Set conversation turn management pattern
- Define interview completion criteria (minimum 6 questions, at least 2 follow-ups)

**Dependencies**: Phase 4 (backend can generate questions, frontend can display them)

---

## Phase 6: Session Persistence

**Goal**: Save interview sessions to database so they can be retrieved later.

**Deliverable**: When an interview completes, the full session (job role, all Q/A turns, timestamps) is saved to SQLite database. Sessions can be retrieved by session ID.

**Components**:
- SQLite database setup and schema
- Session model/schema (job_id, questions, answers, timestamps, session_id)
- Database connection and ORM/sqlite3 integration
- Session save endpoint/logic
- Session retrieval endpoint/logic

**Architectural Decisions**:
- Define database schema for sessions
- Choose database access pattern (raw SQL vs ORM)
- Establish session ID generation strategy
- Set up database initialization and migration approach

**Dependencies**: Phase 5 (interview flow exists, can capture complete session data)

---

## Phase 7: Transcript and Evaluation Display

**Goal**: After interview completion, display full transcript and structured evaluation.

**Deliverable**: When interview ends, user sees:
- Complete transcript showing all Q/A turns in sequence
- Structured evaluation in JSON format containing:
  - Strengths
  - Concerns
  - Overall score
- Evaluation is generated based on the interview conversation

**Components**:
- Evaluation generation logic (using AI/LLM to analyze conversation and produce evaluation)
- Evaluation endpoint/service
- Transcript display component (formatted Q/A list)
- Evaluation display component (formatted JSON or structured view)
- Post-interview results page/section

**Architectural Decisions**:
- Define evaluation schema/structure (strengths array, concerns array, score format)
- Establish evaluation generation approach (prompt engineering, rubric-based)
- Design results page layout
- Choose JSON display format (raw JSON vs formatted UI)

**Dependencies**: Phase 6 (session data is persisted and can be retrieved for evaluation)

---

## Phase 8: Deployment and Hosting Setup

**Goal**: Make the application deployable and accessible via public URL.

**Deliverable**: Application can be deployed to a hosting platform (e.g., Streamlit Cloud, Heroku, Railway, etc.) and accessed via public URL. Both frontend and backend services are properly configured for production deployment. If password protection is used, credentials are documented.

**Components**:
- Docker configuration (if containerization is needed)
- Environment variable configuration
- Deployment configuration files
- Production-ready error handling
- Documentation for deployment process
- Public URL access verification

**Architectural Decisions**:
- Choose hosting platform
- Determine deployment architecture (monolithic vs separate frontend/backend)
- Set up environment configuration management
- Establish production logging and monitoring approach

**Dependencies**: Phase 7 (complete application functionality exists)

---

## Parallel Work Opportunities

- **Phase 3 and Phase 4**: Voice input capture and backend API setup can be developed in parallel once Phase 2 is complete, as they don't depend on each other initially.
- **Phase 6 and Phase 7**: Session persistence and evaluation generation can be developed in parallel once Phase 5 is complete, though evaluation will need session data to be saved first.

---

## Stretch Goals (Post-MVP)

These can be implemented after the core roadmap is complete:

1. **Deterministic interviewer state**: Add "decision panel" showing interviewer's current rubric/signals (skills detected, topics covered, gaps) and reasoning for next question selection.

2. **Job-specific question packs**: Create structured question banks per role (behavioral + technical categories), have AI select from them and generate targeted follow-ups.

3. **Video mode**: Add optional camera input with "video call" layout (voice-driven, video is UX layer only).

4. **Replay + analytics**: Add session history page with interview replay, filtering by role, and per-session metrics (duration, talk ratio, topic coverage, score trend).

