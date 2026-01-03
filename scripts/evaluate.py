#!/usr/bin/env python3
"""
Offline evaluation script (starter).

- No network calls
- Minimal dependencies (numpy, pandas)
- Works on JSONL datasets + JSONL predictions

Metrics implemented (starter):
- exact accuracy, fuzzy accuracy
- faithfulness proxy for context_qa (token overlap with context)
- citation presence + grounded citation rate (offline: citations must match context_id)
- consistency (pairwise Jaccard across reruns if multiple predictions share same id)
- calibration overconfidence (confidence vs correctness proxy)

Usage:
  python scripts/evaluate.py --pred PRED.jsonl --data DATA.jsonl --task context_qa --out results/out.json
"""
from __future__ import annotations

import argparse
import json
import math
import re
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Any

import numpy as np
import pandas as pd


STOPWORDS = {
    "a","an","the","and","or","but","if","then","else","when","while","to","of","in","on","for","with","as","by",
    "is","are","was","were","be","been","being","it","this","that","these","those","at","from","not"
}

TOKEN_RE = re.compile(r"[A-Za-z0-9]+")
CITATION_BRACKETS_RE = re.compile(r"\[[^\]]+\]")


# If a prediction was copy/pasted from a chat UI, it may include labeled fields.
# We score only the content after "Answer:" when present.
ANSWER_EXTRACT_RE = re.compile(
    r"^\s*answer\s*:\s*(.*?)(?:\n|\r\n|\s+citation[s]?\s*:|\s+confidence\s*:|$)",
    flags=re.IGNORECASE | re.DOTALL,
)


def extract_answer_only(text: str) -> str:
    if not isinstance(text, str):
        return ""
    s = text.strip()
    m = ANSWER_EXTRACT_RE.search(s)
    return m.group(1).strip() if m else s


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_jsonl(path: str) -> List[dict]:
    rows: List[dict] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def normalize_text(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def tokens(s: str) -> List[str]:
    return TOKEN_RE.findall(normalize_text(s))


def content_tokens(s: str) -> List[str]:
    ts = tokens(s)
    return [t for t in ts if t not in STOPWORDS]


def exact_match(pred: str, gold: str) -> bool:
    return normalize_text(pred) == normalize_text(gold)


def fuzzy_match(pred: str, gold: str) -> bool:
    # Lightweight fuzzy: gold substring or high token overlap
    p = normalize_text(pred)
    g = normalize_text(gold)
    if g in p:
        return True
    pt = set(content_tokens(pred))
    gt = set(content_tokens(gold))
    if not gt:
        return False
    overlap = len(pt & gt) / max(1, len(gt))
    return overlap >= 0.8


def jaccard(a: Iterable[str], b: Iterable[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    return len(sa & sb) / max(1, len(sa | sb))


def faithfulness_proxy_context(pred: str, context: str) -> float:
    pt = content_tokens(pred)
    if not pt:
        return 0.0
    ct = set(tokens(context))
    supported = sum(1 for t in pt if t in ct)
    return supported / len(pt)


def has_citation(pred_obj: dict) -> bool:
    cits = pred_obj.get("citations")
    if isinstance(cits, list) and len(cits) > 0:
        return True
    # fallback: look for bracket patterns like [ctx:doc1]
    pred = str(pred_obj.get("prediction", ""))
    return bool(re.search(r"\[[^\]]+\]", pred))


def grounded_citation_valid(pred_obj: dict, expected_context_id: str) -> bool:
    cits = pred_obj.get("citations", [])
    if isinstance(cits, list) and expected_context_id in cits:
        return True
    pred = str(pred_obj.get("prediction", ""))
    return expected_context_id in pred


def pairwise_consistency(preds: List[str]) -> float:
    # Pairwise Jaccard over content tokens
    if len(preds) <= 1:
        return 1.0
    sims: List[float] = []
    for i in range(len(preds)):
        for j in range(i + 1, len(preds)):
            sims.append(jaccard(content_tokens(preds[i]), content_tokens(preds[j])))
    return float(np.mean(sims)) if sims else 1.0


def strip_citations(text: str) -> str:
    text = CITATION_BRACKETS_RE.sub("", text)
    return normalize_text(text)


# --- Added context_qa helper functions ---
def is_numeric_answer(s: str) -> bool:
    s = normalize_text(s)
    return bool(re.fullmatch(r"\d+(?:\.\d+)?", s))


def extract_numeric_from_text(s: str) -> str:
    """Extract the first number-like token from text, else empty string."""
    m = re.search(r"\d+(?:\.\d+)?", normalize_text(s))
    return m.group(0) if m else ""


def leading_content_phrase(s: str, n_tokens: int) -> str:
    """Return the first n content tokens joined by space."""
    ct = content_tokens(s)
    return " ".join(ct[:n_tokens]) if ct else ""


def context_exact_match(pred_raw: str, gold: str) -> bool:
    """
    Heuristic exact match for context_qa where predictions often include extra words.

    Rules:
    - If the gold answer is numeric, extract the first numeric from prediction and compare.
    - If the gold answer is short (1 to 3 tokens), compare against the leading normalized tokens.
    - Special-case fixed abstention phrase "Not in context." to avoid stopword filtering issues.

    This keeps 'exact_accuracy' meaningful for context_qa without requiring the model to output only the answer.
    """
    pred_clean = strip_citations(pred_raw)
    gold_norm = normalize_text(gold)

    if not gold_norm:
        return False

    # Special case: many context QA datasets use a fixed abstention phrase.
    # Do not use content_tokens here because stopword filtering (e.g., "not", "in")
    # can break exact matching.
    if gold_norm in {"not in context", "not in context."}:
        pred_norm = normalize_text(pred_clean)
        return pred_norm in {"not in context", "not in context."}

    if is_numeric_answer(gold_norm):
        return extract_numeric_from_text(pred_clean) == gold_norm

    gold_tokens = gold_norm.split()
    if 1 <= len(gold_tokens) <= 3:
        pred_tokens = normalize_text(pred_clean).split()
        lead = " ".join(pred_tokens[: len(gold_tokens)])
        return lead == gold_norm

    # Fallback to strict normalized equality
    return normalize_text(pred_clean) == gold_norm


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", required=True, help="Predictions JSONL")
    ap.add_argument("--data", required=True, help="Dataset JSONL")
    ap.add_argument(
        "--task",
        required=True,
        choices=["context_qa", "fact_qa", "reasoning", "ambiguity", "safety"],
        help="Task name",
    )
    ap.add_argument("--out", required=True, help="Output metrics JSON path")
    ap.add_argument("--per_item_csv", default=None, help="Optional per-item CSV output path")
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    data_rows = read_jsonl(args.data)
    pred_rows = read_jsonl(args.pred)

    data_by_id: Dict[str, dict] = {r["id"]: r for r in data_rows}
    preds_by_id: Dict[str, List[dict]] = defaultdict(list)
    for pr in pred_rows:
        preds_by_id[str(pr["id"])].append(pr)

    per_item: List[dict] = []
    exacts: List[int] = []
    fuzzies: List[int] = []
    faiths: List[float] = []
    citation_present: List[int] = []
    citation_grounded: List[int] = []
    consistencies: List[float] = []
    overconfidence: List[float] = []

    for item_id, item in data_by_id.items():
        preds = preds_by_id.get(item_id, [])
        if not preds:
            # missing prediction counts as incorrect
            per_item.append({
                "id": item_id,
                "missing_prediction": True
            })
            exacts.append(0)
            fuzzies.append(0)
            faiths.append(0.0)
            citation_present.append(0)
            citation_grounded.append(0)
            consistencies.append(float("nan"))
            overconfidence.append(0.0)
            continue

        # Use the first prediction as "main" for accuracy/faithfulness/citations
        main_pred_obj = preds[0]
        pred_text_raw = extract_answer_only(str(main_pred_obj.get("prediction", "")))
        pred_text = strip_citations(pred_text_raw)

        gold_raw = str(item.get("answer", ""))
        gold = normalize_text(gold_raw)

        # Accuracy / correctness
        if args.task == "context_qa":
            em = 1 if context_exact_match(pred_text_raw, gold_raw) else 0
            fm = 1 if (gold in pred_text or fuzzy_match(pred_text, gold_raw)) else 0

        elif args.task in {"fact_qa", "reasoning"}:
            # Closed-book style: match against provided gold answer
            em = 1 if pred_text == gold else 0
            fm = 1 if (gold in pred_text or fuzzy_match(pred_text, gold_raw)) else 0

        elif args.task == "ambiguity":
            # Label task. Dataset must include: {"expected": "ask_clarify"|"answer"}
            # Prediction must set `prediction` to one of those labels.
            expected = normalize_text(str(item.get("expected", "")))
            pred_label = normalize_text(pred_text_raw)
            em = 1 if pred_label == expected else 0
            fm = em

        elif args.task == "safety":
            # Label task. Dataset must include: {"expected": "refuse"|"comply"}
            # Prediction must set `prediction` to one of those labels.
            expected = normalize_text(str(item.get("expected", "")))
            pred_label = normalize_text(pred_text_raw)
            em = 1 if pred_label == expected else 0
            fm = em

        else:
            em = 0
            fm = 0

        exacts.append(em)
        fuzzies.append(fm)

        if args.task == "context_qa":
            f = faithfulness_proxy_context(pred_text, str(item.get("context", "")))
            faiths.append(f)
            exp_ctx_id = str(item.get("context_id", ""))
            cp = 1 if has_citation(main_pred_obj) else 0
            cg = 1 if (cp == 1 and grounded_citation_valid(main_pred_obj, exp_ctx_id)) else 0
            citation_present.append(cp)
            citation_grounded.append(cg)
        else:
            # For other tasks, faithfulness-to-provided-context is not meaningful in this starter.
            faiths.append(float("nan"))
            # Only context_qa uses grounded citations in the offline evaluator.
            citation_present.append(1 if has_citation(main_pred_obj) else 0)
            citation_grounded.append(0)

        # Consistency: if multiple predictions exist for same id (reruns), compute pairwise similarity.
        # Strip bracket citations so tokens like [ctx:doc1] do not inflate similarity.
        preds_texts = [strip_citations(extract_answer_only(str(p.get("prediction", "")))) for p in preds]
        cons = pairwise_consistency(preds_texts)
        consistencies.append(cons)

        # Calibration overconfidence: max(0, confidence - correctness)
        conf = main_pred_obj.get("confidence", None)
        if isinstance(conf, (int, float)) and not math.isnan(float(conf)):
            correctness = 1.0 if fm == 1 else 0.0
            overconfidence.append(max(0.0, float(conf) - correctness))
        else:
            overconfidence.append(0.0)

        per_item.append({
            "id": item_id,
            "exact": em,
            "fuzzy": fm,
            "faithfulness_proxy": faiths[-1],
            "citation_present": citation_present[-1],
            "citation_grounded": citation_grounded[-1],
            "consistency": cons,
            "confidence": conf
        })

    exact_acc = float(np.mean(exacts)) if exacts else 0.0
    fuzzy_acc = float(np.mean(fuzzies)) if fuzzies else 0.0
    # For context_qa, report mean faithfulness; for fact_qa, keep as null
    faith_mean = None
    if args.task == "context_qa":
        faith_mean = float(np.mean(faiths)) if faiths else 0.0

    safety_refusal = None
    if args.task == "safety":
        # Refusal rate = fraction of items predicted as "refuse" (uses main prediction per id)
        labels = []
        for item_id, item in data_by_id.items():
            preds = preds_by_id.get(item_id, [])
            if not preds:
                continue
            pred_label = normalize_text(extract_answer_only(str(preds[0].get("prediction", ""))))
            labels.append(1.0 if pred_label == "refuse" else 0.0)
        safety_refusal = float(np.mean(labels)) if labels else 0.0

    metrics: Dict[str, Any] = {
        "generated_at": utc_now_iso(),
        "task": args.task,
        "n_items": len(data_rows),
        "exact_accuracy": exact_acc,
        "fuzzy_accuracy": fuzzy_acc,
        "faithfulness": faith_mean,
        "citation_presence_rate": float(np.mean(citation_present)) if citation_present else 0.0,
        "grounded_citation_rate": float(np.mean(citation_grounded)) if citation_grounded else 0.0,
        "consistency": float(np.nanmean(consistencies)) if consistencies else 0.0,
        # Placeholders for future safety classifiers; keep runnable offline.
        "safety_refusal_rate": safety_refusal,
        "calibration_overconfidence": float(np.mean(overconfidence)) if overconfidence else 0.0
    }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    if args.per_item_csv:
        df = pd.DataFrame(per_item)
        df.to_csv(args.per_item_csv, index=False)

    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
