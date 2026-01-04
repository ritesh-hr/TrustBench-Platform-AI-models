import os
from openai import AsyncOpenAI
from llm.token_tracker import TokenTracker

client = AsyncOpenAI(
    api_key=os.environ.get("XAI_API_KEY"),
    base_url="https://api.x.ai/v1"
)

tracker = TokenTracker()

async def call_async(
    *,
    prompt: str,
    model: str,
    model_id: str,
    price_per_million: float,
    max_tokens: int = 300,
    temperature: float = 0.2
) -> str:

    response = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature
    )

    if getattr(response, "usage", None):
        tracker.record(
            model_id=model_id,
            prompt_tokens=response.usage.prompt_tokens or 0,
            completion_tokens=response.usage.completion_tokens or 0,
            price_per_million=price_per_million
        )

    return response.choices[0].message.content.strip()
