MODELS = [
    # --------------------
    # OpenAI
    # --------------------
    {
        "provider": "openai",
        "name": "gpt-4o",
        "id": "openai_gpt4o"
    },
    {
        "provider": "openai",
        "name": "gpt-4.1",
        "id": "openai_gpt41"
    },
    {
        "provider": "openai",
        "name": "gpt-5",
        "id": "openai_gpt5"
    },

    # --------------------
    # Anthropic (Claude)
    # --------------------
    # {
    # "id": "claude-3-5-sonnet-20240620",
    # "provider": "anthropic",
    # "name": "claude-3-5-sonnet-20240620",
    # },
    {
        "id": "claude-sonnet-4-5",
        "provider": "anthropic",
        "name": "claude-sonnet-4-5",
    },

    # --------------------
    # Google Gemini
    # --------------------
    {
        "id": "google_gemini_25_pro",
        "provider": "google",
        "name": "gemini-2.5-pro",
    },
    {
        "id": "google_gemini_3_pro_preview",
        "provider": "google",
        "name": "gemini-3-pro-preview",
    },

    # --------------------
    # xAI Grok
    # --------------------
    {
        "provider": "xai",
        "name": "grok-4-1-fast-reasoning",
        "id": "xai_grok_4_1_fast_reasoning",
        "price_per_million_tokens": 5.0
    }
]
