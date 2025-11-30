import os
from enum import Enum
from typing import Optional

from pydantic_settings import BaseSettings


class STTModel(str, Enum):
    WHISPER = "whisper"
    DEEPGRAM = "deepgram"

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Video Journal"
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    # OLLAMA_MODEL: str = "mistral" # Slower, higher quality?
    OLLAMA_MODEL: str = "granite3.1-moe:3b" # Faster
    WHISPER_MODEL: str = "small.en"
    # Preferred device for Whisper: "auto" (default), "mps", "cuda", or "cpu"
    WHISPER_DEVICE: Optional[str] = os.getenv("WHISPER_DEVICE", "auto")
    STT_MODEL: STTModel = STTModel.WHISPER
    DEEPGRAM_API_KEY: Optional[str] = os.getenv("DEEPGRAM_API_KEY", None)

    
    # VAD Settings
    VAD_INTERVAL: float = 0.032 # 512 samples at 16kHz
    SAMPLE_RATE: int = 16000
    VAD_THRESHOLD: float = 0.8 # Higher threshold to reduce false positives
    MIN_AUDIO_LENGTH: float = 0.2  # Minimum audio length to transcribe (seconds)
    VAD_PAUSE_THRESHOLD: float = 0.5 # Silence duration to trigger transcription (seconds) to transcribe
    POST_SPEAKING_SILENCE_THRESHOLD: float = 4.0 # Silence duration to trigger LLM
settings = Settings()
