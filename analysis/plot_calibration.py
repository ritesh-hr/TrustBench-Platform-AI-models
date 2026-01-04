# analysis/plot_calibration.py

import os
import json
import matplotlib.pyplot as plt

RESULTS_DIR = "results"
TASKS = ["safety", "ambiguity", "reasoning"]

def plot_task(model_dir, task):
    cal_path = f"{model_dir}/{task}_calibration.json"
    if not os.path.exists(cal_path):
        print(f"    ⚠️ Missing calibration: {cal_path}")
        return

    with open(cal_path) as f:
        cal = json.load(f)

    bins = cal.get("bins", [])
    if not bins:
        print(f"    ⚠️ No bins for {task}")
        return

    x = [b["confidence_bin"] for b in bins]
    y = [b["consistency_rate"] for b in bins]

    plots_dir = f"{model_dir}/plots"
    os.makedirs(plots_dir, exist_ok=True)

    plt.figure(figsize=(5, 5))
    plt.plot(x, y, marker="o", label="Observed consistency")
    plt.plot([0, 1], [0, 1], linestyle="--", label="Ideal calibration")
    plt.xlabel("Confidence")
    plt.ylabel("Consistency rate")
    plt.title(f"{os.path.basename(model_dir)} — {task}")
    plt.legend()
    plt.tight_layout()

    out = f"{plots_dir}/{task}_calibration.png"
    plt.savefig(out)
    plt.close()

    print(f"    ✓ Plot saved: {out}")

def main():
    print("📊 Generating calibration plots...")

    if not os.path.exists(RESULTS_DIR):
        print("❌ No results directory found.")
        return

    for model in os.listdir(RESULTS_DIR):
        model_dir = f"{RESULTS_DIR}/{model}"
        if not os.path.isdir(model_dir):
            continue

        print(f"\n🧠 Model: {model}")
        for task in TASKS:
            plot_task(model_dir, task)

    print("\n✅ Calibration plotting complete.")

if __name__ == "__main__":
    main()
