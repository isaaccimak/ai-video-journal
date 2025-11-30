from typing import AsyncIterator, Protocol, TypedDict, Literal


class TranscriptEvent(TypedDict):
    type: Literal["transcription"]
    text: str
    final: bool


class BatchSTTProvider(Protocol):
    def transcribe_file(self, file_path: str) -> str:
        ...


class StreamingSTTProvider(Protocol):
    async def stream(self, audio_chunks: AsyncIterator[bytes]) -> AsyncIterator[TranscriptEvent]:
        ...
