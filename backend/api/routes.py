"""API route handlers."""
from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.api.schemas import (
    EndInterviewResponse,
    EvaluationResponse,
    GetSessionResponse,
    StartInterviewRequest,
    StartInterviewResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    TranscribeResponse,
)
from backend.database.session_repository import SessionRepository
from backend.services.evaluation_service import EvaluationService
from backend.services.interview_service import InterviewService
from backend.services.transcription_service import TranscriptionService
from models.job import load_jobs

router = APIRouter()
transcribe_router = APIRouter()

# Initialize services
session_repository = SessionRepository()
evaluation_service = EvaluationService()
interview_service = InterviewService(session_repository=session_repository)
transcription_service = TranscriptionService()


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


@router.get("/{session_id}", response_model=GetSessionResponse)
async def get_session(session_id: str):
    """
    Retrieve a saved interview session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        GetSessionResponse with session data
        
    Raises:
        HTTPException: If session_id is not found
    """
    session = session_repository.get_session(session_id)
    
    if session is None:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")
    
    return GetSessionResponse(
        session_id=session["session_id"],
        job_id=session["job_id"],
        job_title=session["job_title"],
        job_department=session["job_department"],
        conversation_history=session["conversation_history"],
        started_at=session["started_at"],
        ended_at=session["ended_at"],
    )


@router.get("/{session_id}/evaluation", response_model=EvaluationResponse)
async def get_evaluation(session_id: str):
    """
    Get evaluation for a completed interview session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        EvaluationResponse with strengths, concerns, and overall_score
        
    Raises:
        HTTPException: If session not found or not complete
    """
    session = session_repository.get_session(session_id)
    
    if session is None:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")
    
    if session["ended_at"] is None:
        raise HTTPException(status_code=400, detail="Session is not complete")
    
    # Load job to pass to evaluation service
    jobs = load_jobs()
    job = next((j for j in jobs if j.id == session["job_id"]), None)
    
    if job is None:
        # Job was deleted after session was saved - data consistency issue
        raise HTTPException(status_code=422, detail=f"Job not found: {session['job_id']}. The job may have been removed after the interview.")
    
    # Generate evaluation
    evaluation = evaluation_service.evaluate(job, session["conversation_history"])
    
    return EvaluationResponse(**evaluation)


@transcribe_router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribe audio file using OpenAI Whisper API.
    
    Accepts audio files in formats supported by Whisper API:
    mp3, mp4, mpeg, mpga, m4a, wav, webm
    
    File size limit: 25MB (configurable via MAX_AUDIO_SIZE_MB env var)
    
    Returns 503 (Service Unavailable) with Retry-After header for rate limit errors.
    Clients should implement retry logic with exponential backoff.
    
    Args:
        file: Audio file upload (multipart/form-data)
        
    Returns:
        TranscribeResponse with transcribed text
        
    Raises:
        HTTPException 400: If file format is invalid or file is too large
        HTTPException 503: If transcription service is busy (rate limit)
        HTTPException 500: If transcription fails for other reasons
    """
    try:
        # Read file content
        file_content = await file.read()
        filename = file.filename or "audio.webm"
        
        # Transcribe audio
        transcribed_text = transcription_service.transcribe(file_content, filename=filename)
        
        return TranscribeResponse(text=transcribed_text)
        
    except ValueError as e:
        # File format or size validation errors
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        error_msg = str(e).lower()
        # Rate limit / busy errors - return 503 with Retry-After header
        if "busy" in error_msg or "rate" in error_msg:
            raise HTTPException(
                status_code=503,
                detail=str(e),
                headers={"Retry-After": "2"}
            )
        # Other errors (API errors, network errors, etc.)
        raise HTTPException(status_code=500, detail=str(e))

