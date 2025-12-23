"""API route handlers."""
from fastapi import APIRouter, HTTPException
from backend.api.schemas import (
    StartInterviewRequest,
    StartInterviewResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    EndInterviewResponse,
)
from backend.services.interview_service import InterviewService

router = APIRouter()
interview_service = InterviewService()


@router.post("/start", response_model=StartInterviewResponse)
async def start_interview(request: StartInterviewRequest):
    """
    Start a new interview session.
    
    Args:
        request: StartInterviewRequest with job_id
        
    Returns:
        StartInterviewResponse with session_id, question, question_number
        
    Raises:
        HTTPException: If job_id is invalid
    """
    try:
        result = interview_service.start_interview(request.job_id)
        return StartInterviewResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{session_id}/answer", response_model=SubmitAnswerResponse)
async def submit_answer(session_id: str, request: SubmitAnswerRequest):
    """
    Submit an answer and get the next question.
    
    Args:
        session_id: Session identifier
        request: SubmitAnswerRequest with answer
        
    Returns:
        SubmitAnswerResponse with question, question_number, interview_complete
        
    Raises:
        HTTPException: If session_id is invalid or answer is empty
    """
    try:
        result = interview_service.submit_answer(session_id, request.answer)
        return SubmitAnswerResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{session_id}/end", response_model=EndInterviewResponse)
async def end_interview(session_id: str):
    """
    End an interview session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        EndInterviewResponse with session_id and message
        
    Raises:
        HTTPException: If session_id is invalid
    """
    try:
        result = interview_service.end_interview(session_id)
        return EndInterviewResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

