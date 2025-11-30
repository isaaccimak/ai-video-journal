"""Transcription filtering utility."""


class TranscriptionFilter:
    """Filters out invalid or hallucinated transcriptions."""
    
    @staticmethod
    def is_valid(text: str, min_length: int = 2) -> bool:
        """
        Check if transcription text is valid.
        
        Args:
            text: Transcription text to validate
            min_length: Minimum text length (after stripping)
        
        Returns:
            True if text is valid, False otherwise
        """
        if not text:
            return False
        
        stripped = text.strip()
        
        # Check minimum length
        if len(stripped) < min_length:
            return False
        
        # Filter hallucinations (repeated dots)
        if stripped.startswith("..."):
            return False
        
        return True
    
    @staticmethod
    def filter_text(text: str) -> str:
        """
        Clean and filter transcription text.
        
        Args:
            text: Raw transcription text
        
        Returns:
            Cleaned text, or empty string if invalid
        """
        if not TranscriptionFilter.is_valid(text):
            return ""
        return text.strip()
