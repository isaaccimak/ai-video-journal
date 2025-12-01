.PHONY: dev test install docker-up docker-down

# Run the backend server locally (fastest for development)
react:
	cd frontend && npm run dev

ollama:
	ollama serve

dev:
	cd backend && uvicorn app.main:app --reload

# Run the transcription test script
test:
	python test_transcribe.py

# Install dependencies
install:
	pip install -r backend/requirements.txt

# Run with Docker (slower on Mac, good for prod simulation)
docker-up:
	docker compose up --build

# Stop Docker containers
docker-down:
	docker compose down
