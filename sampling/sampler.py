import json
import random

def sample_questions(path: str, k: int, seed: int):
    random.seed(seed)

    items = []
    with open(path) as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue  # skip blank lines
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Invalid JSON on line {lineno} of {path}: {e}"
                )

    if not items:
        raise ValueError(f"No valid items loaded from {path}")

    sampled = random.sample(items, min(k, len(items)))

    normalized = []
    for q in sampled:
        # prompt resolution
        prompt = (
            q.get("prompt")
            or q.get("question")
            or q.get("input")
            or q.get("text")
        )

        if prompt is None:
            raise KeyError(f"No prompt-like field found in dataset item: {q}")

        # label resolution
        label = (
            q.get("expected")
            or q.get("expected_behavior")
            or q.get("answer")
            or q.get("label")
        )

        normalized.append({
            "id": q["id"],
            "prompt": prompt,
            "label": label
        })

    return normalized
