import math
from collections import defaultdict

def calibration_data(records, bins=10):
    buckets = defaultdict(list)

    for r in records:
        conf = r["confidence"]
        correct = r["correct"]
        bucket = min(int(conf * bins), bins - 1)
        buckets[bucket].append((conf, correct))

    ece = 0.0
    curve = []

    for b, vals in buckets.items():
        avg_conf = sum(v[0] for v in vals) / len(vals)
        avg_acc = sum(v[1] for v in vals) / len(vals)
        weight = len(vals) / sum(len(v) for v in buckets.values())
        ece += weight * abs(avg_conf - avg_acc)

        curve.append({
            "bin": b,
            "confidence": round(avg_conf, 3),
            "accuracy": round(avg_acc, 3)
        })

    return round(ece, 4), curve

def consistency(records):
    by_q = defaultdict(list)

    for r in records:
        by_q[r["id"]].append(r["prediction"])

    stable = sum(
        1 for preds in by_q.values()
        if len(set(preds)) == 1
    )

    return round(stable / len(by_q), 4)

def parse_ablation(model_name):
    parts = model_name.split("_")
    return {
        "base_model": parts[0],
        "temp": next((p for p in parts if p.startswith("temp")), None),
        "tokens": next((p for p in parts if p.startswith("tok")), None)
    }
