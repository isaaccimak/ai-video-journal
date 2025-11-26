from typing import Optional

import torch
import whisper

from app.core.config import settings

class STTService:
    def __init__(self):
        # Load model on startup. This might take a while on first run.
        self.device = self._select_device(settings.WHISPER_DEVICE)
        self.device = "cpu" # After testing, Whisper base en on CPU is significantly faster than MPS
        print(f"STT self.device = {self.device}")
        self.model = whisper.load_model(settings.WHISPER_MODEL, device=self.device)

    def transcribe(self, file_path: str) -> str:
        # Suppress FP16 warning on CPU
        fp16 = False if self.device == "cpu" else True
        # result = self.model.transcribe(file_path, fp16=fp16, beam_size=settings.WHISPER_BEAM_SIZE)
        result = self.model.transcribe(file_path, fp16=fp16) # i think default beam is 1, not 5 contrary to what the documentation says
        return result["text"].strip()

    def _select_device(self, preferred: Optional[str]) -> str:
        """Pick the best available device honoring user preference."""
        pref = (preferred or "auto").lower()
        if pref == "mps" or pref == "auto":
            if torch.backends.mps.is_available():
                return "mps"
        if pref == "cuda" or pref == "auto":
            if torch.cuda.is_available():
                return "cuda"
        if pref in {"cpu", "auto"}:
            return "cpu"
        # Fallback if preference is unknown or unavailable
        return "cpu"

stt_service = STTService()
