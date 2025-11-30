"""Audio file handling utility."""
import os
import uuid
import wave
from typing import Optional


class AudioFileHandler:
    """Handles saving audio buffers to temporary WAV files."""
    
    def __init__(self, sample_rate: int = 16000):
        """
        Initialize the audio file handler.
        
        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate = sample_rate
        self.temp_filename: Optional[str] = None
    
    def save_to_wav(self, audio_data: bytes) -> str:
        """
        Save audio data to a temporary WAV file.
        
        Args:
            audio_data: Raw audio bytes (16-bit PCM)
        
        Returns:
            Path to the created WAV file
        """
        self.temp_filename = f"temp_stream_{uuid.uuid4()}.wav"
        
        with wave.open(self.temp_filename, "wb") as wf:
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data)
        
        return self.temp_filename
    
    def cleanup(self) -> None:
        """Remove the temporary WAV file if it exists."""
        if self.temp_filename and os.path.exists(self.temp_filename):
            os.remove(self.temp_filename)
            self.temp_filename = None
