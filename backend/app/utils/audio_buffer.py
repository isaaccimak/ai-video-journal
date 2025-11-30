"""Audio buffer management utility."""


class AudioBufferManager:
    """Manages audio buffer and chunking for VAD processing."""
    
    def __init__(self, chunk_size: int):
        """
        Initialize the audio buffer manager.
        
        Args:
            chunk_size: Size of audio chunks in bytes
        """
        self.buffer = bytearray()
        self.chunk_size = chunk_size
    
    def add_data(self, data: bytes) -> None:
        """
        Add audio data to the buffer.
        
        Args:
            data: Raw audio bytes to add
        """
        self.buffer.extend(data)
    
    def has_chunk(self) -> bool:
        """
        Check if buffer has enough data for a chunk.
        
        Returns:
            True if buffer has at least chunk_size bytes
        """
        return len(self.buffer) >= self.chunk_size
    
    def get_chunk(self) -> bytes:
        """
        Extract and remove a chunk from the buffer.
        
        Returns:
            Audio chunk of chunk_size bytes
        """
        chunk = bytes(self.buffer[:self.chunk_size])
        self.buffer = self.buffer[self.chunk_size:]
        return chunk
    
    def clear(self) -> None:
        """Clear the buffer."""
        self.buffer = bytearray()
