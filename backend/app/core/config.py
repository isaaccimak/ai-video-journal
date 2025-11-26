import os
from typing import Optional

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Video Journal"
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    # OLLAMA_MODEL: str = "mistral" # Slower, higher quality?
    OLLAMA_MODEL: str = "granite3.1-moe:3b" # Faster
    # WHISPER_MODEL: str = "base.en"
    WHISPER_MODEL: str = "tiny.en" # Change model name, look at Whisper library for list
    # Preferred device for Whisper: "auto" (default), "mps", "cuda", or "cpu"
    WHISPER_DEVICE: Optional[str] = os.getenv("WHISPER_DEVICE", "auto")
    # WHISPER_BEAM_SIZE: int = 5

settings = Settings()
