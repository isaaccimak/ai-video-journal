import ollama
from app.core.config import settings

class LLMService:
    def __init__(self):
        self.client = ollama.Client(host=settings.OLLAMA_BASE_URL)

    def generate_question(self, context: str) -> str:
        prompt = f"""
        You are a curious, active listener on a video podcast. The user is recording a monologue. Listen to their story. If they pause or finish a thought, interject with a VERY BRIEF (max 10 words), encouraging question to dig deeper or keep them talking. Do not interrupt mid-sentence. act like a supportive friend.
        User speech: {context}
        """
        
        response = self.client.generate(model=settings.OLLAMA_MODEL, prompt=prompt)
        return response['response'].strip()
