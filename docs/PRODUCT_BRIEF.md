# Product Brief: AI Interviewer Platform

## Project Overview

A lightweight web application that enables candidates to complete AI-driven voice interviews for specific job roles. The platform provides an interactive interview experience where an AI interviewer asks dynamic, context-aware questions that adapt based on candidate responses. Interviews are role-specific, with session recording, transcript generation, and automated evaluation.

## Target Audience

- **Primary**: Job candidates preparing for or participating in interviews
- **Secondary**: Hiring teams evaluating candidate performance through recorded sessions

## Primary Benefits / Features

- **Job Selection**: Browse and select from multiple job postings (minimum 3 roles)
- **Voice-Only Interview**: Natural conversation flow via microphone input
- **Dynamic Questioning**: AI asks 6+ questions with 2+ adaptive follow-ups based on responses
- **Role-Grounded**: Questions tailored to the specific job requirements
- **Session Management**: Automatic session saving and retrieval
- **Transcript & Evaluation**: Complete Q/A transcript and structured evaluation (strengths, concerns, overall score)
- **Clean UX**: Minimal friction interface optimized for interview flow

## High-Level Tech/Architecture

- **Frontend**: Streamlit web application with voice input capabilities
- **Backend**: FastAPI service handling interview orchestration and AI question generation
- **AI Integration**: DSPy + Parakeet for LLM-based interviewer that generates contextual follow-up questions
- **Storage**: SQLite for session persistence of transcripts and evaluations
- **Containerization**: Docker for application packaging and deployment
- **Deployment**: Hosted web application accessible via public URL
- **Architecture**: Single repository, end-to-end hosted solution

