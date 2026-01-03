# TrustBench-Platform (v1)

A lightweight, reproducible starter benchmark for evaluating **trust** in conversational AI platforms:
**faithfulness**, **grounded citations**, **consistency**, **safety**, and **calibration**.

This starter repo is intentionally **offline** and runs on **sample data** (no network calls, no external models).
You can later plug in real model outputs and stronger evaluators (NLI, toxicity classifiers, embedding similarity).

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Evaluate sample predictions on sample context-QA data
python scripts/evaluate.py \
  --pred submissions/sample_predictions.jsonl \
  --data benchmarks/datasets/context/sample_context_qa.jsonl \
  --task context_qa \
  --out results/sample_context_qa_metrics.json

# Validate a submission JSON (schema + required fields)
python scripts/validate_submission.py submissions/sample_submission.json

# Build leaderboard from all submissions/*.json
python scripts/build_leaderboard.py --submissions submissions --out leaderboard/leaderboard.json
```

## What counts as a "submission"?

A submission is a single JSON file in `submissions/` with:
- model metadata (provider, model id, timestamp)
- a task name
- required metrics:
  - `faithfulness`
  - `grounded_citation_rate`
  - `consistency`
  - `safety_refusal_rate`
  - `calibration_overconfidence`

See `schema/submission.schema.json` for the full schema.

## File formats

### Dataset JSONL
Each line is one JSON object. For `context_qa`:
- `id` (string)
- `question` (string)
- `context` (string)
- `answer` (string)
- `context_id` (string; used for offline citation validation)

### Predictions JSONL
Each line is one JSON object:
- `id` (string; must match dataset)
- `prediction` (string)
- optional:
  - `citations` (list of strings, e.g., ["ctx:doc1"])
  - `confidence` (float 0..1)
  - `run_id` (string; use different run_id for reruns to compute consistency)

## Leaderboard flow

1. Add a new `submissions/<name>.json` (must validate).
2. CI validates the JSON on PR.
3. On push, CI rebuilds `leaderboard/leaderboard.json`.

## Frozen model snapshot (Dec 15, 2025)

This repo’s paper/reporting expects you to record exact IDs used at runtime.
Examples (pin exact IDs for reproducibility):
- OpenAI: `gpt-4.1`, `o4-mini`
- Anthropic: pinned snapshots like `claude-sonnet-4-5-20250929`
- Google: `gemini-2.5-pro`
- xAI: `grok-3`
- Perplexity: `sonar-pro`
- Open baselines: `meta-llama/Llama-3.1-8B-Instruct`, `meta-llama/Llama-3.2-3B-Instruct`, `Qwen/Qwen3-30B-A3B-Instruct-2507`

## How to plug in stronger evaluators later

- Replace the faithfulness proxy with an NLI model (entailment) or a claim-checking pipeline.
- Replace token-set Jaccard consistency with embedding similarity.
- Add a safety classifier (toxicity/policy) + human review protocol.
- Add calibration curves (ECE) once you have confidence values at scale.

---

MIT License. See `LICENSE`.
