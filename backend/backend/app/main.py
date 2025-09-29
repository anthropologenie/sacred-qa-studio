from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sacred QA Studio", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"app": "Sacred QA Studio", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "backend"}

@app.get("/api/v1/test")
async def test_endpoint():
    return {"message": "API v1 test endpoint working"}
