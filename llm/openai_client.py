# llm/openai_client.py

from openai import AsyncOpenAI
import os

# Initialize client (API key picked up from environment)
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Models that DO NOT support temperature/top_p (reasoning models)
REASONING_MODELS = {
    "gpt-4.1",
    "gpt-4o",
    "gpt-5",
}

async def call_async(prompt: str, model: str) -> str:
    """
    Unified async OpenAI call.
    Automatically removes unsupported parameters for reasoning models.
    """

    kwargs = {
        "model": model,
        "input": prompt,
    }

    # Only sampling-style models accept temperature
    if model not in REASONING_MODELS:
        kwargs["temperature"] = 0.2

    response = await client.responses.create(**kwargs)

    # Responses API convenience accessor
    return response.output_text
