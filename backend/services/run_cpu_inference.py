
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import onnxruntime as ort
import numpy as np
try:
    from transformers import AutoTokenizer
except Exception:
    AutoTokenizer = None

app = FastAPI()

MODEL_PATH = "models/qwen/model.onnx"
TOKENIZER_ID = "Qwen/Qwen2.5-7B-Instruct"

class PredictionRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 64

@app.get("/health")
def health():
    return {"status": "ok", "provider": "CPUExecutionProvider"}

@app.post("/predict")
def predict(req: PredictionRequest):
    # Minimal safe echo if tokenizer/model absent
    if AutoTokenizer is None:
        return {"text": f"[cpu-echo] {req.prompt[:200]}"}
    try:
        tok = AutoTokenizer.from_pretrained(TOKENIZER_ID, use_fast=True)
        session = ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])
        enc = tok(req.prompt, return_tensors="np")
        input_ids = enc["input_ids"].astype(np.int64)
        attn = enc["attention_mask"].astype(np.int64)
        # NOTE: This is a placeholder loop; real models require proper logits handling
        generated_ids = []
        for _ in range(min(64, req.max_new_tokens)):
            outputs = session.run(None, {"input_ids": input_ids, "attention_mask": attn})
            logits = outputs[0]
            next_token = int(np.argmax(logits[:, -1, :], axis=-1))
            generated_ids.append(next_token)
            input_ids = np.concatenate([input_ids, [[next_token]]], axis=1)
            attn = np.concatenate([attn, [[1]]], axis=1)
        text = tok.decode(generated_ids, skip_special_tokens=True)
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
