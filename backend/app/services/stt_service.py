from typing import AsyncIterator, Optional

from app.core.config import settings, STTModel
from app.services.providers import (
    BatchSTTProvider,
    DeepgramProvider,
    StreamingSTTProvider,
    TranscriptEvent,
    WhisperBatchProvider,
)


class STTService:
    def __init__(self):
        self.batch_provider: BatchSTTProvider
        self.streaming_provider: Optional[StreamingSTTProvider] = None

        # if settings.STT_MODEL == STTModel.DEEPGRAM:
        #     print("Initializing Deepgram STT Provider...")
        #     try:
        #         provider = DeepgramProvider()
        #         self.batch_provider = provider
        #         self.streaming_provider = provider
        #     except Exception as e:
        #         print(f"Failed to init Deepgram: {e}. Falling back to Whisper.")
        #         self.batch_provider = WhisperBatchProvider()
        # else:
        #     print("Initializing Whisper STT Provider...")
        #     self.batch_provider = WhisperBatchProvider()
        try:
            match settings.STT_MODEL:
                case STTModel.DEEPGRAM:
                    print("Initializing Deepgram STT Provider...")
                    provider = DeepgramProvider()
                    self.batch_provider = provider
                    self.streaming_provider = provider
                case STTModel.WHISPER:
                    print("Initializing Whisper STT Provider...")
                    self.batch_provider = WhisperBatchProvider()
                case _:
                    raise ValueError(f"Unsupported STT model: {settings.STT_MODEL}")
        except Exception as e:
            print(f"Failed to init {settings.STT_MODEL}: {e}. Falling back to Whisper.")
            self.batch_provider = WhisperBatchProvider()

    def transcribe_file(self, file_path: str) -> str:
        return self.batch_provider.transcribe_file(file_path)

    async def stream(
        self, audio_chunks: AsyncIterator[bytes]
    ) -> AsyncIterator[TranscriptEvent]:
        if not self.streaming_provider:
            raise NotImplementedError(
                "Streaming transcription not supported for this provider"
            )

        async for event in self.streaming_provider.stream(audio_chunks):
            yield event


stt_service = STTService()
