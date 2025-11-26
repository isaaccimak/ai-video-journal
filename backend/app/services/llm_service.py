import ollama
from app.core.config import settings

class LLMService:
    def __init__(self):
        self.client = ollama.Client(host=settings.OLLAMA_BASE_URL)

    def generate_question(self, context: str) -> str:
        prompt = f"""
        Based on the following user journal entry, 
        ask a thoughtful follow-up question to help them reflect deeper, 
        keep it to 15 words or less:
        Journal Entry: {context}
        Follow-up Question:
        """
        
        response = self.client.generate(model=settings.OLLAMA_MODEL, prompt=prompt)
        return response['response'].strip()

llm_service = LLMService()
