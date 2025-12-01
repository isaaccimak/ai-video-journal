from fastapi import FastAPI
from contextlib import asynccontextmanager
import httpx
import logging
from app.api.routes import router
from app.core.config import settings
from app.services.stt_service import STTService
from app.services.vad_service import VADService
from app.services.llm_service import LLMService

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

async def check_and_pull_model():
    model_name = settings.OLLAMA_MODEL
    base_url = settings.OLLAMA_BASE_URL
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. Check if model exists
            logger.info(f"Checking if model '{model_name}' exists...")
            response = await client.get(f"{base_url}/api/tags")
            response.raise_for_status()
            models = response.json().get("models", [])
            
            model_exists = any(m.get("name") == model_name or m.get("name") == f"{model_name}:latest" for m in models)
            
            if model_exists:
                logger.info(f"Model '{model_name}' found.")
                return

            # 2. Pull model if missing
            logger.info(f"Model '{model_name}' not found. Pulling... This may take a while.")
            
            # Use streaming to prevent timeout on long pulls, though we just wait here
            async with client.stream("POST", f"{base_url}/api/pull", json={"name": model_name}) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        logger.info(f"Pulling: {line}")
            
            logger.info(f"Model '{model_name}' pulled successfully.")
            
        except Exception as e:
            logger.error(f"Failed to check/pull model: {e}")
            # We don't raise here to allow the server to start even if Ollama is down/failing

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await check_and_pull_model()
    app.state.stt_service = STTService()
    app.state.vad_service = VADService()
    app.state.llm_service = LLMService()
    yield
    # Shutdown

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Video Journal Backend"}
