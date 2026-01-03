#!/usr/bin/env python3
"""
Validate a submission JSON against required fields.

This starter avoids heavy dependencies (e.g., jsonschema) and performs
a pragmatic validation aligned to schema/submission.schema.json.

Usage:
  python scripts/validate_submission.py submissions/sample_submission.json
Exit code:
  0 = valid
  1 = invalid
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from typing import Any, Dict


REQUIRED_TOP_LEVEL = ["provider", "model", "timestamp", "task", "metrics", "notes", "run_meta"]
REQUIRED_METRICS = [
    "faithfulness",
    "grounded_citation_rate",
    "consistency",
    "safety_refusal_rate",
    "calibration_overconfidence",
]


def is_iso8601(s: str) -> bool:
    try:
        # Accept common ISO8601 forms; strict parsing varies by libs, so keep simple.
        datetime.fromisoformat(s.replace("Z", "+00:00"))
        return True
    except Exception:
        return False


def fail(msg: str) -> None:
    print(f"[INVALID] {msg}", file=sys.stderr)
    sys.exit(1)


def validate_metrics(metrics: Dict[str, Any]) -> None:
    for k in REQUIRED_METRICS:
        if k not in metrics:
            fail(f"metrics missing required field: {k}")

    # Numeric checks (allow null for placeholders in early stages if desired)
    numeric_fields = ["faithfulness", "grounded_citation_rate", "consistency", "safety_refusal_rate", "calibration_overconfidence"]
    for k in numeric_fields:
        v = metrics.get(k)
        if v is None:
            continue
        if not isinstance(v, (int, float)):
            fail(f"metrics.{k} must be a number or null (got {type(v)})")
        if k != "calibration_overconfidence":
            # Most are rates in [0,1]
            if v < 0.0 or v > 1.0:
                fail(f"metrics.{k} out of range [0,1]: {v}")
        else:
            if v < 0.0:
                fail(f"metrics.{k} must be >= 0: {v}")


def validate_submission(obj: Dict[str, Any]) -> None:
    for k in REQUIRED_TOP_LEVEL:
        if k not in obj:
            fail(f"missing top-level field: {k}")

    if not isinstance(obj["provider"], str) or not obj["provider"].strip():
        fail("provider must be a non-empty string")
    if not isinstance(obj["model"], str) or not obj["model"].strip():
        fail("model must be a non-empty string")
    if not isinstance(obj["timestamp"], str) or not is_iso8601(obj["timestamp"]):
        fail("timestamp must be ISO8601 string (e.g., 2025-12-15T12:00:00Z)")
    if not isinstance(obj["task"], str) or not obj["task"].strip():
        fail("task must be a non-empty string")

    if not isinstance(obj["metrics"], dict):
        fail("metrics must be an object")
    validate_metrics(obj["metrics"])

    if not isinstance(obj["notes"], str):
        fail("notes must be a string")
    if not isinstance(obj["run_meta"], dict):
        fail("run_meta must be an object")


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("submission_json", help="Path to submission JSON")
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    try:
        with open(args.submission_json, "r", encoding="utf-8") as f:
            obj = json.load(f)
    except Exception as e:
        fail(f"failed to read JSON: {e}")

    validate_submission(obj)
    print("[VALID] submission passed validation")
    sys.exit(0)


if __name__ == "__main__":
    main()
