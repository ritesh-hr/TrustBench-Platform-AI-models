# analysis/baseline_deltas.py

import os
import pandas as pd
import json

LEADERBOARD = "leaderboard/leaderboard.csv"
OUT_JSON = "leaderboard/artifacts/baseline_deltas.json"

BASELINE_MODEL = "openai_gpt4o"

def main():
    if not os.path.exists(LEADERBOARD):
        print("⚠️ Leaderboard not found. Skipping baseline deltas.")
        return

    df = pd.read_csv(LEADERBOARD)

    if BASELINE_MODEL is None:
        print("ℹ️ No BASELINE_MODEL set. Skipping baseline deltas.")
        return

    base_rows = df[df["model"] == BASELINE_MODEL]

    if base_rows.empty:
        print(f"⚠️ Baseline model '{BASELINE_MODEL}' not found. Skipping.")
        return

    base = base_rows.iloc[0]

    deltas = []

    for _, row in df.iterrows():
        if row["model"] == BASELINE_MODEL:
            continue

        deltas.append({
            "model": row["model"],
            "delta_safety": row["safety_accuracy"] - base["safety_accuracy"],
            "delta_reasoning": row["reasoning_accuracy"] - base["reasoning_accuracy"],
            "delta_ambiguity": row["ambiguity_accuracy"] - base["ambiguity_accuracy"],
            "delta_consistency": row["consistency"] - base["consistency"],
        })

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump({
            "baseline": BASELINE_MODEL,
            "deltas": deltas
        }, f, indent=2)

    print(f"✓ Baseline deltas written: {OUT_JSON}")

if __name__ == "__main__":
    main()
