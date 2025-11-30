from pydantic import BaseModel

class TranscriptionResponse(BaseModel):
    text: str

class QuestionRequest(BaseModel):
    context: str

class QuestionResponse(BaseModel):
    question: str

class JournalEntryResponse(BaseModel):
    transcription: str
    follow_up_question: str