from fastapi import FastAPI
from pydantic import BaseModel

from inference import inference


app = FastAPI(title="AI Job Dashboard Inference API")


class InferenceRequest(BaseModel):
    prompt: str


@app.get("/")
def root():
    return {"message": "service_up"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/metadata")
def metadata():
    return {"name": "ai-job-dashboard", "description": "AI Job Dashboard RL"}

@app.get("/schema")
def schema():
    return {"action": {}, "observation": {}, "state": {}}

@app.post("/mcp")
def mcp():
    return {"jsonrpc": "2.0"}

@app.post("/state")
def state_env():
    return {"status": "ok"}

@app.post("/ok")
def ok():
    return {"status": "ok"}

@app.post("/reset")
def reset_env():
    return {"status": "ok"}

@app.post("/step")
def step_env():
    return {"status": "ok"}

@app.post("/inference")
def run_inference(req: InferenceRequest):
    return {"output": inference(req.prompt)}
