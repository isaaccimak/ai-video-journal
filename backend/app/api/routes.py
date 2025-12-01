from fastapi import APIRouter, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect, Form, Depends, Request
from app.models.schemas import TranscriptionResponse, QuestionRequest, QuestionResponse, JournalEntryResponse
from app.services.stt_service import STTService
from app.services.vad_service import VADService
from app.services.llm_service import LLMService
import shutil
import os
import uuid

router = APIRouter()

from starlette.requests import HTTPConnection

def get_stt_service(conn: HTTPConnection) -> STTService:
    return conn.app.state.stt_service

def get_vad_service(conn: HTTPConnection) -> VADService:
    return conn.app.state.vad_service

def get_llm_service(conn: HTTPConnection) -> LLMService:
    return conn.app.state.llm_service

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(file: UploadFile = File(...), stt_service: STTService = Depends(get_stt_service)):
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
async def generate_question(request: QuestionRequest, llm_service: LLMService = Depends(get_llm_service)):
    try:
        question = llm_service.generate_question(request.context)
        print(question)
        return QuestionResponse(question=question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-entry", response_model=JournalEntryResponse)
async def process_journal_entry(
    file: UploadFile = File(...),
    stt_service: STTService = Depends(get_stt_service),
    llm_service: LLMService = Depends(get_llm_service),
):
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
async def websocket_endpoint(
    websocket: WebSocket,
    stt_service: STTService = Depends(get_stt_service),
    vad_service: VADService = Depends(get_vad_service),
    llm_service: LLMService = Depends(get_llm_service),
):
    await websocket.accept()
    print("WebSocket connected")
    
    session = JournalingSession(
        stt_service=stt_service,
        vad_service=vad_service,
        llm_service=llm_service,
    )
    
    try:
        while True:
            data = await websocket.receive_bytes()
            
            async for event in session.process_audio(data):
                await websocket.send_json(event)
                
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")


@router.websocket("/ws/audio/stream")
async def websocket_streaming_audio(
    websocket: WebSocket,
    stt_service: STTService = Depends(get_stt_service),
):
    await websocket.accept()

    # if not stt_service.streaming_provider:
    #     await websocket.close(code=4400)
    #     return

    async def audio_chunks():
        try:
            while True:
                data = await websocket.receive_bytes()
                yield data
        except WebSocketDisconnect:
            return

    try:
        async for event in stt_service.stream(audio_chunks()):
            await websocket.send_json(event)
    except WebSocketDisconnect:
        print("Streaming WebSocket disconnected")
    except NotImplementedError as e:
        print(f"Streaming not implemented: {e}")
        await websocket.close(code=1011)
    except Exception as e:
        print(f"WebSocket streaming error: {e}")
        await websocket.close(code=1011)

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
