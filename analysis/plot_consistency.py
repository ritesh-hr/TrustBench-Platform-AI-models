import json
import matplotlib.pyplot as plt

FILE = "leaderboard/artifacts/consistency.json"

def main():
    with open(FILE) as f:
        data = json.load(f)

    models = [d["model"] for d in data]
    scores = [d["consistency"] for d in data]

    plt.figure(figsize=(8, 4))
    plt.bar(models, scores)
    plt.ylabel("Run-to-run consistency")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    plt.savefig("leaderboard/artifacts/consistency.png")
    print("✔ Consistency plot saved")

if __name__ == "__main__":
    main()
