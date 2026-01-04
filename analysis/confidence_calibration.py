import os
import json
import csv
from collections import defaultdict
from datetime import datetime

SUBMISSIONS = "submissions"
RESULTS = "results"
BINS = [i / 10 for i in range(0, 11)]


def bin_conf(c):
    return round(min(max(c, 0.0), 1.0), 1)


def run():
    print("📈 Running confidence calibration...\n")

    for model_id in os.listdir(SUBMISSIONS):
        model_dir = f"{SUBMISSIONS}/{model_id}"
        if not os.path.isdir(model_dir):
            continue

        print(f"📌 Model: {model_id}")
        out_dir = f"{RESULTS}/{model_id}"
        csv_dir = f"{out_dir}/csv"
        os.makedirs(csv_dir, exist_ok=True)

        for task in ["safety", "ambiguity", "reasoning"]:
            path = f"{model_dir}/{task}.jsonl"
            if not os.path.exists(path):
                continue

            bins = defaultdict(lambda: {"correct": 0, "total": 0})

            with open(path) as f:
                for line in f:
                    r = json.loads(line)
                    conf = bin_conf(r["confidence"])
                    correct = r.get("correct", True)
                    bins[conf]["total"] += 1
                    if correct:
                        bins[conf]["correct"] += 1

            rows = []
            for b in sorted(bins):
                acc = bins[b]["correct"] / bins[b]["total"]
                rows.append({
                    "confidence_bin": b,
                    "consistency_rate": round(acc, 3),
                    "count": bins[b]["total"],
                })

            # ---- JSON ----
            with open(f"{out_dir}/{task}_calibration.json", "w") as f:
                json.dump({
                    "generated_at": datetime.utcnow().isoformat(),
                    "task": task,
                    "bins": rows
                }, f, indent=2)

            # ---- CSV ----
            with open(f"{csv_dir}/{task}_calibration.csv", "w", newline="") as f:
                writer = csv.DictWriter(
                    f, fieldnames=["confidence_bin", "consistency_rate", "count"]
                )
                writer.writeheader()
                writer.writerows(rows)

            print(f"  ✔ {task}: {len(rows)} bins")

        print()

    print("✅ Confidence calibration complete.\n")


if __name__ == "__main__":
    run()
