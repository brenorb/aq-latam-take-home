"""Transcription service using OpenAI Whisper API."""
import os
import logging
from io import BytesIO
from typing import BinaryIO, Union
from openai import OpenAI, APIError, RateLimitError, AuthenticationError

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Service for transcribing audio using OpenAI Whisper API."""
    
    # Supported audio formats by Whisper API
    SUPPORTED_FORMATS = {"mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"}
    
    def __init__(self):
        """
        Initialize TranscriptionService.
        
        Reads configuration from environment variables:
        - OPENAI_API_KEY (required): OpenAI API key
        - MAX_AUDIO_SIZE_MB (optional, default: 25): Maximum audio file size in MB
        - OPENAI_MODEL (optional, default: "whisper-1"): Whisper model to use
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(api_key=api_key)
        self.max_audio_size_mb = int(os.getenv("MAX_AUDIO_SIZE_MB", "25"))
        self.model = os.getenv("OPENAI_MODEL", "whisper-1")
        
        logger.info(f"TranscriptionService initialized with model={self.model}, max_size={self.max_audio_size_mb}MB")
    
    def transcribe(self, audio_data: Union[BinaryIO, bytes], filename: str = "audio.webm") -> str:
        """
        Transcribe audio file using OpenAI Whisper API.
        
        Args:
            audio_data: Audio file data (file-like object or bytes)
            filename: Name of the audio file (used to determine format)
            
        Returns:
            Transcribed text string
            
        Raises:
            ValueError: If file format is unsupported or file size exceeds limit
            Exception: If OpenAI API call fails (wraps OpenAI exceptions)
        """
        # Validate file format
        file_extension = filename.split(".")[-1].lower() if "." in filename else ""
        if file_extension not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported audio format: {file_extension}. "
                f"Supported formats: {', '.join(sorted(self.SUPPORTED_FORMATS))}"
            )
        
        # Handle bytes input
        if isinstance(audio_data, bytes):
            audio_file = BytesIO(audio_data)
            audio_file.name = filename
        else:
            audio_file = audio_data
            # Reset file position to beginning
            if hasattr(audio_file, "seek"):
                audio_file.seek(0)
        
        # Validate file size
        if hasattr(audio_file, "seek") and hasattr(audio_file, "tell"):
            audio_file.seek(0, 2)  # Seek to end
            file_size = audio_file.tell()
            audio_file.seek(0)  # Reset to beginning
            
            max_size_bytes = self.max_audio_size_mb * 1024 * 1024
            if file_size > max_size_bytes:
                raise ValueError(
                    f"File size ({file_size / (1024 * 1024):.2f}MB) exceeds maximum "
                    f"allowed size ({self.max_audio_size_mb}MB)"
                )
        
        try:
            logger.info(f"Transcribing audio file: {filename}")
            
            # Call OpenAI Whisper API
            transcript = self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
                language="en",  # Optional: can be auto-detected
                response_format="text"
            )
            
            transcribed_text = transcript.text if hasattr(transcript, "text") else str(transcript)
            logger.info(f"Transcription successful: {len(transcribed_text)} characters")
            
            return transcribed_text
            
        except RateLimitError as e:
            logger.error(f"OpenAI rate limit error: {e}")
            raise Exception("Transcription service is busy. Please wait a moment and try again.") from e
        except AuthenticationError as e:
            logger.error(f"OpenAI authentication error: {e}")
            raise Exception("Transcription service authentication failed. Please contact support.") from e
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise Exception(f"Transcription service error: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error during transcription: {e}")
            raise Exception(f"Transcription failed: {str(e)}") from e

