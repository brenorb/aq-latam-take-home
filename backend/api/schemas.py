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



