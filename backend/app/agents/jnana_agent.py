from sqlalchemy.orm import Session
from sqlalchemy import text as sql_text  # ← Rename to avoid conflict
from typing import Dict, Any
from datetime import datetime
import json
import uuid

class JnanaAgent:
    """Validation agent with qa_logs integration"""
    
    def __init__(self, db: Session, agent_id: str = "jnana-validator-v1"):
        self.db = db
        self.agent_id = agent_id
    
    def validate_sankalpa(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        execution_id = str(uuid.uuid4())
        errors = []
        
        text = request_data.get("text", "")  # ← This was shadowing the import
        if not text:
            errors.append("Sankalpa text is required")
        elif len(text) < 3:
            errors.append("Text too short (min 3 chars)")
        elif len(text) > 5000:
            errors.append("Text exceeds 5000 characters")
        
        context = request_data.get("context", "")
        if context and len(context) > 2000:
            errors.append("Context exceeds 2000 characters")
        
        result = {
            "valid": len(errors) == 0,
            "errors": errors,
            "metadata": {
                "agent_id": self.agent_id,
                "execution_id": execution_id,
                "validated_at": datetime.utcnow().isoformat(),
                "text_length": len(text),
                "has_context": bool(context)
            }
        }
        
        # Log to qa_logs
        log_query = sql_text("""
            INSERT INTO app.qa_logs (id, agent_id, request_json, response_json, created_at)
            VALUES (:id, :agent_id, CAST(:req AS jsonb), CAST(:resp AS jsonb), NOW())
        """)
        self.db.execute(log_query, {
            "id": execution_id,
            "agent_id": self.agent_id,
            "req": json.dumps(request_data),
            "resp": json.dumps(result)
        })
        
        return result
