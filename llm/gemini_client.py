import asyncio
from google import genai

# Client reads GOOGLE_API_KEY from env
client = genai.Client()


# -------------------------
# Model capability guards
# -------------------------

def supports_temperature(model_name: str) -> bool:
    # Preview models do not support temperature
    return not model_name.endswith("preview")


# -------------------------
# Response extraction (CRITICAL FIX)
# -------------------------

def extract_text(response) -> str:
    """
    Robust Gemini response extraction.
    Handles MAX_TOKENS silent refusals.
    """

    # 1. Normal text path
    if hasattr(response, "text") and response.text:
        return response.text.strip()

    # 2. Candidate parts
    if hasattr(response, "candidates") and response.candidates:
        for candidate in response.candidates:
            content = getattr(candidate, "content", None)
            if not content:
                continue

            parts = getattr(content, "parts", None)
            if parts:
                for part in parts:
                    text = getattr(part, "text", None)
                    if text:
                        return text.strip()

            # 3. Silent refusal / MAX_TOKENS
            finish = getattr(candidate, "finish_reason", None)
            if str(finish) == "FinishReason.MAX_TOKENS":
                return "__BLOCKED__"

    return ""



# -------------------------
# Sync call (executor-safe)
# -------------------------

def _sync_call(prompt: str, model: str, max_tokens: int) -> str:
    config = {
        "max_output_tokens": max_tokens,
    }

    if supports_temperature(model):
        config["temperature"] = 0.2

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=config,
    )
   
    return extract_text(response)


# -------------------------
# Async wrapper
# -------------------------

async def call_async(prompt: str, model: str, max_tokens: int = 1024) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        _sync_call,
        prompt,
        model,
        max_tokens,
    )
