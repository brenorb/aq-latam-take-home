"""FastAPI application entry point."""
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router, transcribe_router
from backend.database.db import init_db

# Configuration from environment variables
# LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Default: INFO
# CORS_ORIGINS: Comma-separated list of allowed origins, or "*" for all. Default: http://localhost:8501
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8501")

# Configure logging
log_level = getattr(logging, LOG_LEVEL, logging.INFO)
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
logger.setLevel(log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    logger.info("Initializing database...")
    init_db()
    logger.info("Application startup complete")
    yield
    # Shutdown
    logger.info("Application shutdown")


app = FastAPI(
    title="AI Interviewer Platform API",
    description="Backend API for AI-driven interview platform",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
if CORS_ORIGINS == "*":
    cors_origins = ["*"]
else:
    cors_origins = [origin.strip() for origin in CORS_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(router, prefix="/api/interviews", tags=["interviews"])
app.include_router(transcribe_router, prefix="/api", tags=["transcription"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AI Interviewer Platform API"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

