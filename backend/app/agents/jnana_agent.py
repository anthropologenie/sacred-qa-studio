"""JnanaAgent - Validation agent for Sacred QA Studio"""
from typing import Dict, Any
from datetime import datetime

class JnanaAgent:
    """Simple validation agent"""
    
    def __init__(self, agent_id: str = "jnana-validator-v1"):
        self.agent_id = agent_id
    
    def validate_sankalpa(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate sankalpa request
        Returns: {"valid": bool, "errors": list, "metadata": dict}
        """
        errors = []
        
        # Validation rules
        text = request_data.get("text", "")
        if not text:
            errors.append("Sankalpa text is required")
        elif len(text) < 3:
            errors.append("Text too short (min 3 chars)")
        elif len(text) > 5000:
            errors.append("Text exceeds 5000 characters")
        
        context = request_data.get("context", "")
        if context and len(context) > 2000:
            errors.append("Context exceeds 2000 characters")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "metadata": {
                "agent_id": self.agent_id,
                "validated_at": datetime.utcnow().isoformat(),
                "text_length": len(text),
                "has_context": bool(context)
            }
        }
