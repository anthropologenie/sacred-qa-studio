from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4
import httpx
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session as DBSession
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://admin:secure_password_123@postgres:5432/ai_qa_platform")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# FastAPI app
app = FastAPI(title="Sacred QA Backend", version="0.1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schemas
class SankalpaCreate(BaseModel):
    text: str
    context: Optional[str] = None

class SankalpaResponse(BaseModel):
    id: UUID
    text: str
    context: Optional[str]
    created_at: datetime

# Health endpoint
@app.get("/health")
def health():
    return {"status": "healthy", "service": "backend"}

# Sankalpa endpoint
@app.post("/sankalpa", response_model=SankalpaResponse)
def create_sankalpa(payload: SankalpaCreate, db: DBSession = Depends(get_db)):
    sankalpa_id = uuid4()
    query = text("""
        INSERT INTO app.sankalpa (id, text, context, created_at)
        VALUES (:id, :text, :context, NOW())
        RETURNING id, text, context, created_at
    """)
    
    result = db.execute(
        query,
        {"id": str(sankalpa_id), "text": payload.text, "context": payload.context}
    )
    db.commit()
    
    row = result.fetchone()
    return {
        "id": row[0],
        "text": row[1],
        "context": row[2],
        "created_at": row[3]
    }

# QA endpoint (inference proxy)
@app.post("/qa")
async def qa_proxy(payload: dict, db: DBSession = Depends(get_db)):
    inference_url = os.getenv("AI_SERVICE_HOST", "ai-inference")
    inference_port = os.getenv("AI_SERVICE_PORT", "8001")
    
    async with httpx.AsyncClient(timeout=60) as client:
        try:
            response = await client.post(
                f"http://{inference_url}:{inference_port}/infer",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Inference service error: {str(e)}")
    
    # Log to qa_logs
    log_query = text("""
        INSERT INTO app.qa_logs (id, agent_id, model, device, request_json, response_json, created_at)
        VALUES (:id, :agent_id, :model, :device, :request::jsonb, :response::jsonb, NOW())
    """)
    
    import json
    db.execute(log_query, {
        "id": str(uuid4()),
        "agent_id": "mock-inference",
        "model": "mock",
        "device": "cpu",
        "request": json.dumps(payload),
        "response": json.dumps(result)
    })
    db.commit()
    
    return {"agent": "mock-inference", "data": result}
