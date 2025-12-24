"""API request/response schemas."""
from pydantic import BaseModel, Field


class ConversationEntrySchema(BaseModel):
    """Schema for a conversation history entry."""
    question: str = Field(..., description="The question that was asked")
    answer: str = Field(..., description="The answer provided by the user")
    question_number: int = Field(..., description="The question number (1-indexed)")
    is_followup: bool = Field(..., description="Whether this question was a follow-up to the previous answer")


class StartInterviewRequest(BaseModel):
    """Request schema for starting an interview."""
    job_id: str = Field(..., description="ID of the job to interview for")


class StartInterviewResponse(BaseModel):
    """Response schema for starting an interview."""
    session_id: str = Field(..., description="Unique session identifier")
    question: str = Field(..., description="First interview question")
    question_number: int = Field(..., description="Current question number (1-indexed)")
    conversation_history: list[ConversationEntrySchema] = Field(default_factory=list, description="Conversation history (empty at start)")


class SubmitAnswerRequest(BaseModel):
    """Request schema for submitting an answer."""
    answer: str = Field(..., min_length=1, description="User's answer text")


class SubmitAnswerResponse(BaseModel):
    """Response schema for submitting an answer."""
    question: str | None = Field(None, description="Next question (None if interview complete)")
    question_number: int = Field(..., description="Current question number")
    interview_complete: bool = Field(..., description="Whether interview is complete")
    conversation_history: list[ConversationEntrySchema] = Field(..., description="Updated conversation history")


class EndInterviewResponse(BaseModel):
    """Response schema for ending an interview."""
    session_id: str = Field(..., description="Session identifier")
    message: str = Field(..., description="Success message")


class GetSessionResponse(BaseModel):
    """Response schema for retrieving a session."""
    session_id: str = Field(..., description="Unique session identifier")
    job_id: str = Field(..., description="Job identifier")
    job_title: str = Field(..., description="Job title")
    job_department: str = Field(..., description="Job department")
    conversation_history: list[ConversationEntrySchema] = Field(..., description="Conversation history")
    started_at: str = Field(..., description="ISO datetime when interview started")
    ended_at: str | None = Field(None, description="ISO datetime when interview ended")


class EvaluationResponse(BaseModel):
    """Response schema for evaluation endpoint."""
    strengths: list[str] = Field(..., description="List of candidate strengths")
    concerns: list[str] = Field(..., description="List of concerns or areas for improvement")
    overall_score: float = Field(..., description="Overall score from 0.0 to 100.0")


class TranscribeResponse(BaseModel):
    """Response schema for transcription endpoint."""
    text: str = Field(..., description="Transcribed text from audio")

