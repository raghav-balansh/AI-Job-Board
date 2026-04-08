import os

from openai import OpenAI


API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

# Optional: only needed when using from_docker_image()
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")

def _get_client() -> OpenAI:
    # All LLM calls use this OpenAI client configured by env vars.
    return OpenAI(
        base_url=API_BASE_URL,
        api_key=HF_TOKEN,
    )


def from_docker_image() -> OpenAI:
    """Optional helper for local OpenAI-compatible docker gateway."""
    if not LOCAL_IMAGE_NAME:
        raise ValueError("LOCAL_IMAGE_NAME is required for from_docker_image()")
    local_base = os.getenv("LOCAL_API_BASE_URL", "http://localhost:8000/v1")
    return OpenAI(base_url=local_base, api_key=HF_TOKEN)


def inference(prompt: str) -> str:
    if not HF_TOKEN:
        raise ValueError("HF_TOKEN is required and must be set in environment variables.")

    print("START")
    print("STEP: preparing request")
    client = _get_client()
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
    )
    result = (response.choices[0].message.content or "").strip()
    print("STEP: generation complete")
    print("END")
    return result


if __name__ == "__main__":
    output = inference("What is the capital of France?")
    print(output)
