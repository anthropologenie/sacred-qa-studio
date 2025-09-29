from fastapi import FastAPI, Request
from pydantic import BaseModel
from datetime import datetime, timezone
import uvicorn

app = FastAPI()

class PredictionRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 16

@app.get("/health")
def health():
    return {"status": "healthy", "service": "ai-inference"}

@app.get("/vcv")
def vcv():
    return {
        "schema_version": "0.1.0",
        "model_path": "mock://no-model",
        "device": "mock",
        "supported_formats": ["chat_completion"],
        "max_tokens": 8192,
        "health_check_url": "/health",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "inputs": [],
        "outputs": []
    }

@app.post("/predict")
def predict(req: PredictionRequest):
    # Placeholder - replace with real model later
    return {"text": f"ECHO: {req.prompt[:100]}..."}

@app.post("/infer")
async def infer(req: Request):
    # Generic inference endpoint for QA tests
    body = await req.json()
    return {"ok": True, "echo": body}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
