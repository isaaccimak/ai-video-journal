from fastapi import APIRouter, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect, Form
from app.models.schemas import TranscriptionResponse, QuestionRequest, QuestionResponse, JournalEntryResponse
from app.services.stt_service import stt_service
from app.services.llm_service import llm_service
import shutil
import os
import uuid

router = APIRouter()

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(file: UploadFile = File(...)):
    file_ext = os.path.splitext(file.filename)[1] if file.filename else ".wav"
    temp_filename = f"temp_{uuid.uuid4()}{file_ext}"
    try:
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = os.path.getsize(temp_filename)
        print(f"Saved temp file: {temp_filename}, Size: {file_size} bytes")
        
        text = stt_service.transcribe_file(temp_filename)
        
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
    file_ext = os.path.splitext(file.filename)[1] if file.filename else ".wav"
    temp_filename = f"temp_{uuid.uuid4()}{file_ext}"
    try:
        # 1. Save and Transcribe
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        transcription = stt_service.transcribe_file(temp_filename)
        
        # 2. Generate Question
        question = llm_service.generate_question(transcription)
        
        return JournalEntryResponse(
            transcription=transcription,
            generated_question=question
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)


from app.services.journaling_session import JournalingSession

@router.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connected")
    
    session = JournalingSession()
    
    try:
        while True:
            data = await websocket.receive_bytes()
            
            async for event in session.process_audio(data):
                await websocket.send_json(event)
                
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")

from app.services.video_service import video_service

@router.post("/save-video")
async def save_video(file: UploadFile = File(...), save_path: str = Form(...)):
    """
    Save and convert uploaded video file.
    
    Args:
        file: Uploaded video file (WebM format)
        save_path: Desired filename for the saved video
        
    Returns:
        dict: Success message and path to saved file
    """
    try:
        # Validate filename
        if not save_path:
            raise HTTPException(status_code=400, detail="Filename is required")
        
        # Delegate to service
        final_path = video_service.save_and_convert_video(file.file, save_path)
        
        return {"message": "Video saved successfully", "path": final_path}
        
    except Exception as e:
        print(f"Error saving video: {e}")
        raise HTTPException(status_code=500, detail=str(e))
