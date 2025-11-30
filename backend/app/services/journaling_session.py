import asyncio
from typing import AsyncGenerator, Dict, Any

from app.core.config import settings
from app.services.vad_service import vad_service
from app.services.stt_service import stt_service
from app.services.llm_service import llm_service
from app.utils.audio_buffer import AudioBufferManager
from app.utils.audio_file import AudioFileHandler
from app.utils.silence_detector import SilenceDetector
from app.utils.transcription_filter import TranscriptionFilter


class JournalingSession:
    """Manages a journaling session with audio processing, transcription, and question generation."""
    
    def __init__(self):
        """Initialize the journaling session with utility components."""
        # Calculate chunk size based on VAD interval
        chunk_size = int(settings.VAD_INTERVAL * settings.SAMPLE_RATE * 2)
        
        # Initialize utility components
        self.buffer_manager = AudioBufferManager(chunk_size)
        self.audio_handler = AudioFileHandler(settings.SAMPLE_RATE)
        self.silence_detector = SilenceDetector()
        self.transcription_filter = TranscriptionFilter()
        
        # Session state
        self.speech_buffer = bytearray()
        self.accumulated_transcription = ""

    async def process_audio(self, data: bytes) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Process incoming audio data and yield events.
        
        Args:
            data: Raw audio bytes from the client
        
        Yields:
            Dict containing event type and data (vad, transcription, or question)
        """
        self.buffer_manager.add_data(data)

        # Process chunks of specific size for VAD
        while self.buffer_manager.has_chunk():
            chunk = self.buffer_manager.get_chunk()
            is_speech_chunk = vad_service.is_speech(chunk)

            if is_speech_chunk:
                # Speech detected
                if self.silence_detector.mark_speech():
                    yield {"type": "vad", "active": True}
                
                self.speech_buffer.extend(chunk)
            else:
                # Silence detected
                if self.silence_detector.mark_silence():
                    yield {"type": "vad", "active": False}

                silence_duration = self.silence_detector.get_silence_duration()

                # 1. STT Trigger (Short pause)
                if (self.silence_detector.is_speaking and 
                    self.silence_detector.is_silence_threshold_met(settings.VAD_PAUSE_THRESHOLD) and 
                    len(self.speech_buffer) > 0):
                    
                    print(f"Silence ({silence_duration:.2f}s) > {settings.VAD_PAUSE_THRESHOLD}s, transcribing...")
                    
                    # Filter short audio to avoid transcribing clicks/pops
                    min_bytes = int(settings.MIN_AUDIO_LENGTH * settings.SAMPLE_RATE * 2)
                    if len(self.speech_buffer) < min_bytes:
                        print(f"Ignoring short audio segment (< {settings.MIN_AUDIO_LENGTH}s)")
                        self.speech_buffer = bytearray()
                        self.silence_detector.reset()
                        vad_service.reset()
                        continue

                    # Save buffer to temp file and transcribe
                    try:
                        temp_filename = self.audio_handler.save_to_wav(bytes(self.speech_buffer))
                        
                        # Transcribe (run in thread pool to avoid blocking)
                        text = await asyncio.to_thread(stt_service.transcribe_file, temp_filename)
                        print(f"Transcribed: {text}")

                        # Filter and validate transcription
                        if self.transcription_filter.is_valid(text):
                            self.accumulated_transcription += text + " "
                            yield {
                                "type": "transcription",
                                "text": text
                            }
                    except Exception as e:
                        print(f"Transcription Error: {e}")
                    finally:
                        self.audio_handler.cleanup()

                    # Reset speech buffer
                    self.speech_buffer = bytearray()
                    self.silence_detector.reset()
                    vad_service.reset()

                # 2. LLM Trigger (Long pause)
                if (len(self.accumulated_transcription.strip()) > 0 and 
                    self.silence_detector.is_silence_threshold_met(settings.POST_SPEAKING_SILENCE_THRESHOLD)):
                    
                    print(f"Silence ({silence_duration:.2f}s) > {settings.POST_SPEAKING_SILENCE_THRESHOLD}s, generating question...")

                    # Generate question asynchronously
                    context = self.accumulated_transcription.strip()
                    self.accumulated_transcription = ""  # Clear to avoid double triggering

                    try:
                        question = await asyncio.to_thread(llm_service.generate_question, context)
                        print(f"Generated Question: {question}")

                        yield {
                            "type": "question",
                            "text": question
                        }
                    except Exception as e:
                        print(f"LLM Error: {e}")
