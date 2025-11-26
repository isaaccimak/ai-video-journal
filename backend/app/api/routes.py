from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import TranscriptionResponse, QuestionRequest, QuestionResponse, JournalEntryResponse
from app.services.stt_service import stt_service
from app.services.llm_service import llm_service
import shutil
import os
import uuid

router = APIRouter()

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(file: UploadFile = File(...)):
    temp_filename = f"temp_{uuid.uuid4()}.wav"
    try:
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        text = stt_service.transcribe(temp_filename)
        return TranscriptionResponse(text=text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

@router.post("/generate-question", response_model=QuestionResponse)
async def generate_question(request: QuestionRequest):
    try:
        question = llm_service.generate_question(request.context)
        print(question)
        return QuestionResponse(question=question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-entry", response_model=JournalEntryResponse)
async def process_journal_entry(file: UploadFile = File(...)):
    temp_filename = f"temp_{uuid.uuid4()}.wav"
    try:
        # 1. Save and Transcribe
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        transcription = stt_service.transcribe(temp_filename)
        
        # 2. Generate Question
        question = llm_service.generate_question(transcription)
        
        return JournalEntryResponse(
            transcription=transcription,
            follow_up_question=question
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
