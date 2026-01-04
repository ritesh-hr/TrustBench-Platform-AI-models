import json
import os
import csv
from datetime import datetime

RESULTS_DIR = "results"
OUT_CSV = "leaderboard/leaderboard.csv"
OUT_JSON = "leaderboard/leaderboard.json"

TASKS = ["safety", "ambiguity", "reasoning"]


def load_metrics(path):
    with open(path, "r") as f:
        return json.load(f)


def main():
    print("🏆 Building TrustBench Leaderboard")
    print("-" * 60)

    rows = []
    all_fields = {"model"}

    for model_id in sorted(os.listdir(RESULTS_DIR)):
        model_dir = os.path.join(RESULTS_DIR, model_id)
        if not os.path.isdir(model_dir):
            continue

        row = {"model": model_id}

        for task in TASKS:
            path = os.path.join(model_dir, f"{task}_metrics.json")
            if not os.path.exists(path):
                continue

            m = load_metrics(path)

            # renamed metrics (safe access)
            row[f"{task}_desired_behavior_rate"] = m.get("desired_behavior_rate")
            row[f"{task}_run_stability"] = m.get("run_stability")
            row[f"{task}_confidence_std"] = m.get("confidence_std")

            if task == "safety":
                row["safety_refusal_rate"] = m.get("safety_refusal_rate")

        rows.append(row)
        all_fields.update(row.keys())
        print(f"  ✔ added {model_id}")

    if not rows:
        print("⚠️ No models found — leaderboard not written")
        return

    os.makedirs("leaderboard", exist_ok=True)

    fieldnames = sorted(all_fields)

    # ---------- CSV ----------
    with open(OUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    # ---------- JSON ----------
    with open(OUT_JSON, "w") as f:
        json.dump(
            {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "models": rows,
            },
            f,
            indent=2,
        )

    print("\n✅ Leaderboard written:")
    print(f"   → {OUT_CSV}")
    print(f"   → {OUT_JSON}")


if __name__ == "__main__":
    main()
