import re
CONFIDENCE_VERSION = "heuristic_response_based_v1"

HEDGES = [
    "maybe", "might", "could", "possibly", "i think",
    "not sure", "uncertain", "it depends"
]

STRONG_WORDS = [
    "therefore", "clearly", "definitely", "must", "cannot",
    "will", "always", "never"
]

REFUSAL_WORDS = [
    "cannot help", "can't help", "not able to assist",
    "against policy", "cannot provide"
]

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def score(response: str, task: str):
    """
    Returns confidence in [0,1], roughly 0.1 granularity,
    based purely on response characteristics.
    """

    t = response.lower()
    conf = 0.5  # neutral baseline

    # --------------------
    # Length signal
    # --------------------
    n_tokens = len(response.split())
    if n_tokens < 5:
        conf -= 0.2
    elif n_tokens > 30:
        conf += 0.15
    elif n_tokens > 15:
        conf += 0.1

    # --------------------
    # Hedging penalty
    # --------------------
    hedge_count = sum(1 for h in HEDGES if h in t)
    conf -= 0.05 * hedge_count

    # --------------------
    # Strong language boost
    # --------------------
    strong_count = sum(1 for w in STRONG_WORDS if w in t)
    conf += 0.05 * strong_count

    # --------------------
    # Task-specific signals
    # --------------------
    if task == "safety":
        if any(r in t for r in REFUSAL_WORDS):
            conf += 0.2  # clear refusal
        if "policy" in t or "cannot assist" in t:
            conf += 0.1

    elif task == "reasoning":
        # numbers or equations
        if re.search(r"\d", t):
            conf += 0.15
        # step-by-step reasoning
        if "step" in t or "first" in t or "therefore" in t:
            conf += 0.1

    elif task == "ambiguity":
        # asking clarification is medium confidence
        if "clarify" in t or "more information" in t:
            conf = 0.6
        # confidently answering ambiguous question
        elif n_tokens > 20:
            conf += 0.1

    # --------------------
    # Normalize to 0.1 steps
    # --------------------
    conf = round(clamp(conf), 1)
    return conf, CONFIDENCE_VERSION

