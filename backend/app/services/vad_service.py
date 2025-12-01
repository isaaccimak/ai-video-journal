import torch
import numpy as np
from app.core.config import settings

class VADService:
    def __init__(self):
        self.model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                           model='silero_vad',
                                           force_reload=False,
                                           trust_repo=True)
        (self.get_speech_timestamps,
         self.save_audio,
         self.read_audio,
         self.VADIterator,
         self.collect_chunks) = utils
        
        self.model.to("cpu") # VAD is fast enough on CPU
        self.vad_iterator = self.VADIterator(self.model)
        
        # State for stream processing
        self.buffer = bytearray()
        self.speech_buffer = bytearray()
        self.is_speaking = False
        self.chunk_size = int(settings.VAD_INTERVAL * settings.SAMPLE_RATE * 2)

    def is_speech(self, audio_chunk: bytes) -> bool:
        """
        Check if the given audio chunk contains speech.
        Assumes 16kHz sample rate, mono, 16-bit PCM.
        """
        # Convert bytes to float32 tensor
        audio_int16 = np.frombuffer(audio_chunk, dtype=np.int16)
        audio_float32 = audio_int16.astype(np.float32) / 32768.0
        tensor = torch.from_numpy(audio_float32)
        
        # Silero expects a batch dimension: (1, N)
        if tensor.dim() == 1:
            tensor = tensor.unsqueeze(0)

        speech_prob = self.model(tensor, settings.SAMPLE_RATE).item()
        return speech_prob > settings.VAD_THRESHOLD



    def reset(self):
        self.vad_iterator.reset_states()
        self.buffer = bytearray()
        self.speech_buffer = bytearray()
        self.is_speaking = False
