from fastapi import FastAPI
from pydantic import BaseModel

from inference import inference


app = FastAPI(title="AI Job Dashboard Inference API")


class InferenceRequest(BaseModel):
    prompt: str


@app.get("/")
def root():
    return {"message": "service_up"}


@app.post("/ok")
def ok():
    # Required by automated checker: POST /ok must succeed.
    return {"status": "ok"}


@app.post("/inference")
def run_inference(req: InferenceRequest):
    return {"output": inference(req.prompt)}
