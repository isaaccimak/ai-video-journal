import os
from typing import AsyncIterator

import httpx

from app.core.config import settings
from app.services.providers.types import BatchSTTProvider, StreamingSTTProvider, TranscriptEvent


class DeepgramProvider(BatchSTTProvider, StreamingSTTProvider):
    def __init__(self):
        self.api_key = settings.DEEPGRAM_API_KEY
        if not self.api_key:
            raise ValueError("DEEPGRAM_API_KEY is not set in configuration")
        self.base_url = "https://api.deepgram.com/v1/listen"

    def transcribe_file(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "audio/wav",
        }

        params = {
            "model": "nova-2",
            "smart_format": "true",
            "punctuate": "true",
            "language": "en",
        }

        with open(file_path, "rb") as audio_file:
            response = httpx.post(
                self.base_url,
                headers=headers,
                params=params,
                content=audio_file,
                timeout=60.0,
            )

        response.raise_for_status()
        data = response.json()

        try:
            transcript = data["results"]["channels"][0]["alternatives"][0]["transcript"]
            return transcript.strip()
        except (KeyError, IndexError):
            print(f"Unexpected Deepgram response format: {data}")
            return ""

    async def stream(self, audio_chunks: AsyncIterator[bytes]) -> AsyncIterator[TranscriptEvent]:
        # TODO: implement Deepgram WebSocket streaming
        raise NotImplementedError("Streaming transcription not implemented for Deepgram")
