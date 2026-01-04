import os
import json
import csv
from collections import defaultdict, Counter
from datetime import datetime

SUBMISSIONS = "submissions"
RESULTS = "results"
RUNS = 5


def load_task(model_id, task):
    path = f"{SUBMISSIONS}/{model_id}/{task}.jsonl"
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))
    return rows


def compute_consistency(rows):
    by_id = defaultdict(list)
    for r in rows:
        by_id[r["id"]].append(r["prediction"])

    per_item = {}
    for qid, preds in by_id.items():
        counts = Counter(preds)
        per_item[qid] = max(counts.values()) / len(preds)

    overall = sum(per_item.values()) / len(per_item) if per_item else 0.0
    return overall, per_item


def run():
    print("🔁 Running run-to-run consistency analysis...\n")

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

            rows = load_task(model_id, task)
            overall, per_item = compute_consistency(rows)

            # ---- JSON ----
            metrics = {
                "generated_at": datetime.utcnow().isoformat(),
                "task": task,
                "consistency": round(overall, 4),
                "n_items": len(per_item),
            }

            with open(f"{out_dir}/{task}_consistency.json", "w") as f:
                json.dump(metrics, f, indent=2)

            # ---- CSV ----
            with open(f"{csv_dir}/{task}_consistency.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["id", "consistency"])
                for qid, score in per_item.items():
                    writer.writerow([qid, round(score, 3)])

            print(f"  ✔ {task}: consistency={round(overall,3)}")

        print()

    print("✅ Run consistency analysis complete.\n")


if __name__ == "__main__":
    run()
