import asyncio
# from llm.openai_client import call_async as openai_call
# from llm.anthropic_client import call_async as anthropic_call
# from llm.gemini_client import call_async as gemini_call
# from llm.xai_client import call_async as grok_call

from llm.model_registry import MODELS

MODEL_INDEX = {m["name"]: m for m in MODELS}

async def call_model(provider: str, model_name: str, prompt: str):
    model_cfg = MODEL_INDEX[model_name]

    if provider == "xai":
        from llm.xai_client import call_async as grok_call

        return await grok_call(
            prompt=prompt,
            model=model_name,
            model_id=model_cfg["id"],
            price_per_million=model_cfg["price_per_million_tokens"]
        )

    if provider == "openai":
        from llm.openai_client import call_async as openai_call
        return await openai_call(prompt, model_name)

    if provider == "anthropic":
        from llm.anthropic_client import call_async as anthropic_call
        return await anthropic_call(prompt, model_name)

    if provider == "google":
        from llm.gemini_client import call_async as gemini_call
        return await gemini_call(prompt, model_name)

    raise ValueError(f"Unknown provider: {provider}")
