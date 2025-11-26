import whisper
from app.core.config import settings

class STTService:
    def __init__(self):
        # Load model on startup. This might take a while on first run.
        self.model = whisper.load_model(settings.WHISPER_MODEL)

    def transcribe(self, file_path: str) -> str:
        result = self.model.transcribe(file_path)
        return result["text"].strip()

stt_service = STTService()
