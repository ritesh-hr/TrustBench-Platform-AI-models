# analysis/generate_benchmark_summary.py

import os
import pandas as pd
from dotenv import load_dotenv

from llm.dispatcher_async import call_model
from llm.model_registry import MODELS

# 🔑 ensure API keys are loaded for post-processing & UI
load_dotenv()

SUMMARY_CACHE = "leaderboard/artifacts/benchmark_summary.md"


def pick_best_llm():
    """
    Pick strongest available LLM automatically.
    Priority: OpenAI > Claude > Gemini > Grok
    """
    priority = ["openai", "anthropic", "google", "xai"]
    for p in priority:
        for m in MODELS:
            if m["provider"] == p:
                return m
    return None


async def generate_summary():
    if not os.path.exists("leaderboard/leaderboard.csv"):
        return "⚠️ Leaderboard not found."

    df = pd.read_csv("leaderboard/leaderboard.csv")

    model = pick_best_llm()
    if not model:
        return "⚠️ No LLM available for summary."

    prompt = f"""
You are an AI evaluation expert.

Below is a benchmark leaderboard table.
Summarize key insights in Markdown.

Include:
- 🥇 Best model per task
- ⚖️ Strengths and weaknesses
- 🔁 Stability vs confidence observations
- 🚨 Notable anomalies

Leaderboard table:
{df.to_markdown(index=False)}
"""

    try:
        text = await call_model(
            model["provider"],
            model["name"],
            prompt
        )
    except Exception as e:
        return f"⚠️ Summary generation failed: {e}"

    os.makedirs("leaderboard/artifacts", exist_ok=True)
    with open(SUMMARY_CACHE, "w") as f:
        f.write(text)

    return text


def load_cached_summary():
    if os.path.exists(SUMMARY_CACHE):
        with open(SUMMARY_CACHE) as f:
            return f.read()
    return None
