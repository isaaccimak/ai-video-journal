"""Silence detection utility."""
import time
from typing import Optional


class SilenceDetector:
    """Tracks silence duration and speaking state."""
    
    def __init__(self):
        """Initialize the silence detector."""
        self.is_speaking = False
        self.silence_start_time: Optional[float] = None
    
    def mark_speech(self) -> bool:
        """
        Mark that speech is detected.
        
        Returns:
            True if speech just started (transition from silence)
        """
        speech_just_started = not self.is_speaking
        self.is_speaking = True
        self.silence_start_time = None
        return speech_just_started
    
    def mark_silence(self) -> bool:
        """
        Mark that silence is detected.
        
        Returns:
            True if silence just started (transition from speech)
        """
        current_time = time.time()
        silence_just_started = False
        
        if self.silence_start_time is None:
            self.silence_start_time = current_time
            if self.is_speaking:
                silence_just_started = True
        
        return silence_just_started
    
    def get_silence_duration(self) -> float:
        """
        Get the current silence duration.
        
        Returns:
            Silence duration in seconds, or 0 if not in silence
        """
        if self.silence_start_time is None:
            return 0.0
        return time.time() - self.silence_start_time
    
    def is_silence_threshold_met(self, threshold: float) -> bool:
        """
        Check if silence duration exceeds a threshold.
        
        Args:
            threshold: Silence threshold in seconds
        
        Returns:
            True if silence duration >= threshold
        """
        return self.get_silence_duration() >= threshold
    
    def reset(self) -> None:
        """Reset the detector state."""
        self.is_speaking = False
        self.silence_start_time = None
