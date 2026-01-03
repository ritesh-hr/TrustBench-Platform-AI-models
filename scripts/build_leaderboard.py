#!/usr/bin/env python3
"""
Aggregate submissions into a simple leaderboard.

- Reads all *.json in --submissions directory
- Validates required fields (lightweight)
- Sorts by (task asc, faithfulness desc)
- Writes leaderboard JSON

Usage:
  python scripts/build_leaderboard.py --submissions submissions --out leaderboard/leaderboard.json
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List

# Allow running as a script from repo root: python scripts/build_leaderboard.py ...
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from scripts.validate_submission import validate_submission  # reuse


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--submissions", required=True, help="Directory containing submission JSON files")
    ap.add_argument("--out", required=True, help="Output leaderboard JSON path")
    return ap.parse_args()


def safe_float(x: Any, default: float = -1.0) -> float:
    if isinstance(x, (int, float)):
        return float(x)
    return default


def main() -> None:
    args = parse_args()
    paths = sorted(glob.glob(os.path.join(args.submissions, "*.json")))
    entries: List[Dict[str, Any]] = []

    for p in paths:
        with open(p, "r", encoding="utf-8") as f:
            obj = json.load(f)

        # Validate using the same rules as CI
        validate_submission(obj)

        m = obj["metrics"]
        entries.append({
            "file": os.path.basename(p),
            "provider": obj["provider"],
            "model": obj["model"],
            "timestamp": obj["timestamp"],
            "task": obj["task"],
            "metrics": m
        })

    entries.sort(key=lambda e: (e["task"], -safe_float(e["metrics"].get("faithfulness"), -1.0)))

    out_obj = {
        "generated_at": utc_now_iso(),
        "entries": entries
    }

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, indent=2)

    print(f"Wrote leaderboard with {len(entries)} entries -> {args.out}")


if __name__ == "__main__":
    main()
