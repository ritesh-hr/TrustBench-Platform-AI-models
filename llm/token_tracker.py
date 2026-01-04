from collections import defaultdict
from typing import Dict


class TokenTracker:
    """
    Tracks token usage and estimated cost per model.
    Pricing is assumed to be PER MILLION TOKENS.
    """

    def __init__(self):
        self.usage: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "cost_usd": 0.0
            }
        )

    def record(
        self,
        model_id: str,
        prompt_tokens: int,
        completion_tokens: int,
        price_per_million: float
    ) -> None:
        """
        Record token usage for a single request.

        Args:
            model_id: internal model identifier
            prompt_tokens: number of input tokens
            completion_tokens: number of output tokens
            price_per_million: USD cost per 1,000,000 tokens
        """
        total = prompt_tokens + completion_tokens
        cost = (total / 1_000_000) * price_per_million

        u = self.usage[model_id]
        u["prompt_tokens"] += int(prompt_tokens)
        u["completion_tokens"] += int(completion_tokens)
        u["total_tokens"] += int(total)
        u["cost_usd"] += float(cost)

    def summary(self) -> Dict[str, Dict[str, float]]:
        """
        Returns a JSON-serializable summary of usage.
        """
        return {
            model_id: {
                "prompt_tokens": int(v["prompt_tokens"]),
                "completion_tokens": int(v["completion_tokens"]),
                "total_tokens": int(v["total_tokens"]),
                "cost_usd": round(v["cost_usd"], 6)
            }
            for model_id, v in self.usage.items()
        }

    def reset(self) -> None:
        """
        Clears all tracked usage (useful between runs).
        """
        self.usage.clear()
