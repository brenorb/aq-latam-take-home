"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router

app = FastAPI(
    title="AI Interviewer Platform API",
    description="Backend API for AI-driven interview platform",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(router, prefix="/api/interviews", tags=["interviews"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AI Interviewer Platform API"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

