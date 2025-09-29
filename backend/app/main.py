from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4, UUID
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
import httpx, os, json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://admin:secure_password_123@postgres:5432/ai_qa_platform")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

app = FastAPI(title="Sacred QA Backend")

# Store inference capabilities
app.inference_capabilities = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def harvest_vcv():
    """Gate 2: Harvest VCV from inference service on startup"""
    inference_url = os.getenv("INFERENCE_URL", f"http://{os.getenv('AI_SERVICE_HOST', 'ai-inference')}:{os.getenv('AI_SERVICE_PORT', '8001')}")    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{inference_url}/vcv")
            response.raise_for_status()
            vcv_data = response.json()
            
            # Store in app state
            app.inference_capabilities = vcv_data
            
            # Persist to database
            db = SessionLocal()
            try:
                vcv_query = text("""
                    INSERT INTO app.inference_capabilities 
                    (id, vcv_data, harvested_at)
                    VALUES (:id, CAST(:vcv_data AS jsonb), NOW())
                """)
                db.execute(vcv_query, {
                    "id": str(uuid4()),
                    "vcv_data": json.dumps(vcv_data)
                })
                db.commit()
                logger.info(f"✅ VCV harvested: {vcv_data.get('device', 'unknown')}")
            finally:
                db.close()
                
    except Exception as e:
        logger.warning(f"⚠️  Could not harvest VCV: {e}")

@app.get("/health")
def health():
    return {"status":"healthy","service":"backend"}

class SankalpaCreate(BaseModel):
    text: str
    context: Optional[str] = None

class SankalpaResponse(BaseModel):
    id: UUID
    text: str
    context: Optional[str]
    created_at: datetime

@app.post("/sankalpa", response_model=SankalpaResponse)
def create_sankalpa(body: SankalpaCreate, db: Session =Depends(get_db)):
    q = text("""
      INSERT INTO app.sankalpa (id, text, context, created_at)
      VALUES (:id, :text, :context, NOW())
      RETURNING id, text, context, created_at
    """)
    sid = str(uuid4())
    row = db.execute(q, {"id": sid, "text": body.text, "context": body.context}).fetchone()
    db.commit()
    return {"id": row[0], "text": row[1], "context": row[2], "created_at": row[3]}

@app.post("/qa")
async def qa_proxy(payload: dict, db: Session = Depends(get_db)):
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
            raise HTTPException(status_code=503, detail=f"Inference error: {str(e)}")

    log_query = text("""
        INSERT INTO app.qa_logs (id, agent_id, model, device, request_json, response_json, created_at)
        VALUES (:id, :agent_id, :model, :device, CAST(:request AS jsonb), CAST(:response AS jsonb), NOW())
    """)

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
