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
        import asyncio
        from deepgram import (
            DeepgramClient,
            DeepgramClientOptions,
            LiveTranscriptionEvents,
            LiveOptions,
        )

        # Create a queue to bridge callbacks to async iterator
        queue = asyncio.Queue()
        loop = asyncio.get_running_loop()

        try:
            # Initialize Deepgram Client
            deepgram = DeepgramClient(self.api_key)

            # Create a websocket connection to Deepgram
            dg_connection = deepgram.listen.asynclive.v("1")

            # Define event handlers
            async def on_message(self, result, **kwargs):
                if result.channel and result.channel.alternatives:
                    transcript = result.channel.alternatives[0].transcript
                    if transcript:
                        await queue.put(TranscriptEvent(
                            text=transcript,
                            is_final=result.is_final
                        ))

            async def on_metadata(self, metadata, **kwargs):
                # print(f"Metadata: {metadata}")
                pass

            async def on_error(self, error, **kwargs):
                print(f"Deepgram Error: {error}")
                # Signal error to the consumer? For now just log.

            # Register handlers
            dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
            dg_connection.on(LiveTranscriptionEvents.Metadata, on_metadata)
            dg_connection.on(LiveTranscriptionEvents.Error, on_error)

            # Configure options
            options = LiveOptions(
                model="nova-2",
                language="en-US",
                smart_format=True,
                interim_results=True,
                punctuate=True,
                encoding="linear16",
                channels=1,
                sample_rate=16000,
            )

            # Start the connection
            if await dg_connection.start(options) is False:
                print("Failed to start Deepgram connection")
                return

            # Start a task to send audio chunks
            async def send_audio():
                try:
                    async for chunk in audio_chunks:
                        await dg_connection.send(chunk)
                except Exception as e:
                    print(f"Error sending audio to Deepgram: {e}")
                finally:
                    await dg_connection.finish()
                    # Signal end of stream to queue
                    await queue.put(None)

            send_task = asyncio.create_task(send_audio())

            # Yield events from queue
            while True:
                event = await queue.get()
                if event is None:
                    break
                yield event

            await send_task

        except Exception as e:
            print(f"Deepgram streaming error: {e}")
            raise
