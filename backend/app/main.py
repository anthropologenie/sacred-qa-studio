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

# CREATE - with lineage tracking
@app.post("/sankalpa", response_model=SankalpaResponse)
def create_sankalpa(body: SankalpaCreate, db: Session = Depends(get_db)):
    from app.agents.jnana_agent import JnanaAgent
    from datetime import datetime
    
    # Generate IDs
    contact_id = str(uuid4())
    root_lineage_id = str(uuid4())
    sankalpa_id = str(uuid4())
    
    # 1. Log sacred contact (API request)
    contact_query = text("""
        INSERT INTO app.sacred_contacts 
        (contact_id, request_payload, api_endpoint, timestamp)
        VALUES (:id, CAST(:payload AS jsonb), :endpoint, NOW())
    """)
    db.execute(contact_query, {
        "id": contact_id,
        "payload": json.dumps({"text": body.text, "context": body.context}),
        "endpoint": "/sankalpa"
    })
    
    # 2. Create root lineage entry
    root_lineage_query = text("""
        INSERT INTO app.request_lineage 
        (lineage_id, agent_name, operation_type, metadata)
        VALUES (:id, :agent, :op, CAST(:meta AS jsonb))
    """)
    db.execute(root_lineage_query, {
        "id": root_lineage_id,
        "agent": "api-gateway",
        "op": "sankalpa_create",
        "meta": json.dumps({"contact_id": contact_id})
    })
    
    # 3. Run JnanaAgent validation
    agent = JnanaAgent()
    validation_start = datetime.utcnow()
    validation = agent.validate_sankalpa({"text": body.text, "context": body.context})
    validation_duration = int((datetime.utcnow() - validation_start).total_seconds() * 1000)
    
    # 4. Log validation in lineage
    validation_lineage_query = text("""
        INSERT INTO app.request_lineage 
        (lineage_id, parent_lineage_id, agent_name, operation_type, metadata, duration_ms, success)
        VALUES (:id, :parent, :agent, :op, CAST(:meta AS jsonb), :duration, :success)
    """)
    db.execute(validation_lineage_query, {
        "id": str(uuid4()),
        "parent": root_lineage_id,
        "agent": "jnana-validator-v1",
        "op": "validate_sankalpa",
        "meta": json.dumps(validation["metadata"]),
        "duration": validation_duration,
        "success": validation["valid"]
    })
    
    # 5. Return error if validation failed
    if not validation["valid"]:
        # Update contact with error response
        error_response_query = text("""
            UPDATE app.sacred_contacts 
            SET response_payload = CAST(:response AS jsonb), status_code = :status
            WHERE contact_id = :id
        """)
        db.execute(error_response_query, {
            "id": contact_id,
            "response": json.dumps({
                "errors": validation["errors"],
                "lineage_id": root_lineage_id,
                "status": "validation_failed"
            }),
            "status": 400
        })
        db.commit()
        raise HTTPException(
            status_code=400, 
            detail={"errors": validation["errors"], "lineage_id": root_lineage_id}
        )
    
    # 6. Insert sankalpa
    sankalpa_query = text("""
        INSERT INTO app.sankalpa (id, text, context, created_at)
        VALUES (:id, :text, :context, NOW())
        RETURNING id, text, context, created_at
    """)
    row = db.execute(sankalpa_query, {
        "id": sankalpa_id,
        "text": body.text,
        "context": body.context
    }).fetchone()
    
    # 7. Log sankalpa creation in lineage
    insert_lineage_query = text("""
        INSERT INTO app.request_lineage 
        (lineage_id, parent_lineage_id, agent_name, operation_type, metadata)
        VALUES (:id, :parent, :agent, :op, CAST(:meta AS jsonb))
    """)
    db.execute(insert_lineage_query, {
        "id": str(uuid4()),
        "parent": root_lineage_id,
        "agent": "db-writer",
        "op": "insert_sankalpa",
        "meta": json.dumps({"sankalpa_id": sankalpa_id})
    })
    
    # 8. Update contact with response
    update_contact_query = text("""
        UPDATE app.sacred_contacts 
        SET response_payload = CAST(:response AS jsonb), status_code = :status
        WHERE contact_id = :id
    """)
    db.execute(update_contact_query, {
        "id": contact_id,
        "response": json.dumps({
            "id": sankalpa_id,
            "lineage_id": root_lineage_id,
            "status": "created"
        }),
        "status": 201
    })
    
    db.commit()
    
    return {
        "id": row[0], 
        "text": row[1], 
        "context": row[2], 
        "created_at": row[3]
    }

# LIST - new
@app.get("/sankalpa")
def list_sankalpa(q: Optional[str] = None, limit: int = 100, db: Session = Depends(get_db)):
    """List sankalpas with optional text search"""
    if q:
        query = text("""
            SELECT id, text, context, status, created_at 
            FROM app.sankalpa 
            WHERE text ILIKE :search
            ORDER BY created_at DESC 
            LIMIT :limit
        """)
        rows = db.execute(query, {"search": f"%{q}%", "limit": limit}).fetchall()
    else:
        query = text("""
            SELECT id, text, context, status, created_at 
            FROM app.sankalpa 
            ORDER BY created_at DESC 
            LIMIT :limit
        """)
        rows = db.execute(query, {"limit": limit}).fetchall()
    
    return [
        {"id": r[0], "text": r[1], "context": r[2], "status": r[3], "created_at": r[4]}
        for r in rows
    ]

# READ - new
@app.get("/sankalpa/{sid}")
def get_sankalpa(sid: UUID, db: Session = Depends(get_db)):
    """Get single sankalpa by ID"""
    query = text("""
        SELECT id, text, context, status, is_active, created_at, updated_at, completed_at
        FROM app.sankalpa 
        WHERE id = :sid
    """)
    row = db.execute(query, {"sid": str(sid)}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Sankalpa not found")
    
    return {
        "id": row[0], "text": row[1], "context": row[2], "status": row[3],
        "is_active": row[4], "created_at": row[5], "updated_at": row[6], "completed_at": row[7]
    }

# UPDATE - new
@app.patch("/sankalpa/{sid}")
def update_sankalpa(sid: UUID, body: dict, db: Session = Depends(get_db)):
    """Update sankalpa fields"""
    updates = []
    params = {"sid": str(sid)}
    
    if "text" in body:
        updates.append("text = :text")
        params["text"] = body["text"]
    if "context" in body:
        updates.append("context = :context")
        params["context"] = body["context"]
    if "status" in body:
        updates.append("status = :status")
        params["status"] = body["status"]
        if body["status"] == "completed":
            updates.append("completed_at = NOW()")
    
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    updates.append("updated_at = NOW()")
    query = text(f"""
        UPDATE app.sankalpa 
        SET {', '.join(updates)}
        WHERE id = :sid
        RETURNING id, text, context, status, created_at
    """)
    
    row = db.execute(query, params).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Sankalpa not found")
    
    db.commit()
    return {"id": row[0], "text": row[1], "context": row[2], "status": row[3], "created_at": row[4]}

# DELETE - new
@app.delete("/sankalpa/{sid}")
def delete_sankalpa(sid: UUID, db: Session = Depends(get_db)):
    """Delete sankalpa"""
    query = text("DELETE FROM app.sankalpa WHERE id = :sid RETURNING id")
    row = db.execute(query, {"sid": str(sid)}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Sankalpa not found")
    db.commit()
    return {"ok": True, "deleted_id": row[0]}


# LINEAGE - new
@app.get("/lineage/{lineage_id}")
def get_lineage_tree(lineage_id: UUID, db: Session = Depends(get_db)):
    """Get full lineage tree for a request"""
    query = text("""
        WITH RECURSIVE lineage_tree AS (
            -- Base case: get the root node
            SELECT lineage_id, parent_lineage_id, agent_name, operation_type,
                   timestamp, metadata, duration_ms, success, 0 as depth
            FROM app.request_lineage
            WHERE lineage_id = :lineage_id
            
            UNION ALL
            
            -- Recursive case: get all children
            SELECT rl.lineage_id, rl.parent_lineage_id, rl.agent_name, rl.operation_type,
                   rl.timestamp, rl.metadata, rl.duration_ms, rl.success, lt.depth + 1
            FROM app.request_lineage rl
            INNER JOIN lineage_tree lt ON rl.parent_lineage_id = lt.lineage_id
        )
        SELECT * FROM lineage_tree ORDER BY timestamp
    """)
    
    rows = db.execute(query, {"lineage_id": str(lineage_id)}).fetchall()
    
    if not rows:
        raise HTTPException(status_code=404, detail="Lineage not found")
    
    return {
        "lineage_id": str(lineage_id),
        "total_operations": len(rows),
        "tree": [
            {
                "lineage_id": str(r[0]),
                "parent_lineage_id": str(r[1]) if r[1] else None,
                "agent_name": r[2],
                "operation_type": r[3],
                "timestamp": str(r[4]),
                "metadata": r[5],
                "duration_ms": r[6],
                "success": r[7],
                "depth": r[8]
            }
            for r in rows
        ]
    }

# QA LOGS LIST - new
@app.get("/qa_logs")
def list_qa_logs(limit: int = 50, db: Session = Depends(get_db)):
    """List recent QA logs"""
    query = text("""
        SELECT id, agent_id, model, device, request_json, response_json, created_at
        FROM app.qa_logs
        ORDER BY created_at DESC
        LIMIT :limit
    """)
    rows = db.execute(query, {"limit": limit}).fetchall()
    return [
        {
            "id": r[0], "agent_id": r[1], "model": r[2], "device": r[3],
            "request": r[4], "response": r[5], "created_at": r[6]
        }
        for r in rows
    ]

# QA proxy - existing
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


@app.post("/tests/run")
def run_tests(db: Session = Depends(get_db)):
    """Queue test execution (stub implementation)"""
    query = text("""
        SELECT id, name, description 
        FROM app.test_cases 
        WHERE COALESCE(status, '') != 'passed'
        LIMIT 20
    """)
    rows = db.execute(query).fetchall()
    return {
        "status": "queued",
        "test_count": len(rows),
        "tests": [{"id": r[0], "name": r[1], "description": r[2]} for r in rows]
    }
