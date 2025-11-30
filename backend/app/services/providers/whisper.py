import torch
import whisper
from transformers import pipeline

from app.core.config import settings
from app.services.providers.types import BatchSTTProvider


class WhisperBatchProvider(BatchSTTProvider):
    def __init__(self):
        print("Loading Hugging Face Whisper model...")

        device = -1
        if torch.cuda.is_available():
            device = 0
        elif torch.backends.mps.is_available():
            device = "mps"

        print(f"Using device: {device}")

        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=f"openai/whisper-{settings.WHISPER_MODEL}",
            device=device,
            chunk_length_s=30,
        )

    def transcribe_file(self, file_path: str) -> str:
        audio = whisper.load_audio(file_path)
        result = self.pipe(audio)
        return result["text"].strip()
