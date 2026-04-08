FROM python:3.11-slim

WORKDIR /app

# Install only the lightweight server dependencies (no torch/streamlit needed)
RUN pip install --no-cache-dir \
    fastapi>=0.115.0 \
    uvicorn>=0.30.0 \
    openai>=1.40.0 \
    pydantic>=2.0.0

# Copy only the server files needed for inference
COPY inference.py .
COPY server.py .

ENV PYTHONUNBUFFERED=1

EXPOSE 7860

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "7860"]
