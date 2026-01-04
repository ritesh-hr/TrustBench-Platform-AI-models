from anthropic import AsyncAnthropic

client = AsyncAnthropic()

def extract_text(response):
    if not hasattr(response, "content") or not response.content:
        return ""

    texts = []
    for block in response.content:
        if block.type == "text" and hasattr(block, "text"):
            texts.append(block.text)

    return "".join(texts).strip()


async def call_async(prompt: str, model: str, max_tokens: int = 1024) -> str:
    response = await client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=0.2,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    text = extract_text(response) 
    return text
