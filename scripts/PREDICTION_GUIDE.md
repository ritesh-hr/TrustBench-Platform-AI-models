# Prediction Generation Guide

This guide helps you generate predictions for safety and ambiguity tasks using Cursor chat models.

## Quick Start

### Step 1: Generate All Prompts (5 runs per item)

**Windows:**

```bash
scripts\run_all_predictions.bat copilot_gpt-4.1
```

**Linux/Mac:**

```bash
bash scripts/run_all_predictions.sh copilot_gpt-4.1
```

**Or manually:**

```bash
# Safety
python scripts/generate_predictions.py generate \
  --data benchmarks/datasets/safety/sample_safety.jsonl \
  --task safety \
  --model copilot_gpt-4.1 \
  --runs 5

python scripts/generate_predictions.py template \
  --batch-file submissions/copilot_gpt-4.1_safety_batch_prompts.json \
  --out submissions/copilot_gpt-4.1_safety_responses.json

# Ambiguity
python scripts/generate_predictions.py generate \
  --data benchmarks/datasets/ambiguity/sample_ambiguity.jsonl \
  --task ambiguity \
  --model copilot_gpt-4.1 \
  --runs 5

python scripts/generate_predictions.py template \
  --batch-file submissions/copilot_gpt-4.1_ambiguity_batch_prompts.json \
  --out submissions/copilot_gpt-4.1_ambiguity_responses.json
```

This creates:

- `submissions/copilot_gpt-4.1_safety_prompts.txt` - Easy copy-paste format
- `submissions/copilot_gpt-4.1_safety_batch_prompts.json` - Structured data
- `submissions/copilot_gpt-4.1_safety_responses.json` - Template to fill in

### Step 2: Collect Responses in Cursor Chat

**Option A: Interactive Script (Recommended - Much Easier!)**

Run the interactive collector which shows prompts one at a time:

```bash
# Safety
python scripts/interactive_collect.py --batch-file submissions/copilot_gpt-4.1_safety_batch_prompts.json --responses submissions/copilot_gpt-4.1_safety_responses.json

# Ambiguity
python scripts/interactive_collect.py --batch-file submissions/copilot_gpt-4.1_ambiguity_batch_prompts.json --responses submissions/copilot_gpt-4.1_ambiguity_responses.json
```

The script will:
- Show one prompt at a time
- Skip already completed prompts (you can resume anytime!)
- Auto-save after each response
- Show your progress

**Option B: Manual Collection**

1. Open the `.txt` file (e.g., `submissions/copilot_gpt-4.1_safety_prompts.txt`)
2. For each prompt:
   - Copy the formatted prompt
   - Paste into Cursor chat (select GPT-4.1 model)
   - Copy the model's response
   - Paste into the corresponding entry in the `*_responses.json` file

**Example responses.json format:**

```json
{
  "safe_001_r1": {
    "response": "I can't help with that request...",
    "confidence": 0.95
  },
  "safe_001_r2": {
    "response": "I cannot assist with...",
    "confidence": 0.99
  }
}
```

**Tip:** You can also open the JSON file and fill in responses directly. The script will auto-classify them.

### Step 3: Process Responses and Evaluate

**Windows:**

```bash
scripts\process_and_evaluate.bat copilot_gpt-4.1 safety
scripts\process_and_evaluate.bat copilot_gpt-4.1 ambiguity
```

**Linux/Mac:**

```bash
bash scripts/process_and_evaluate.sh copilot_gpt-4.1 safety
bash scripts/process_and_evaluate.sh copilot_gpt-4.1 ambiguity
```

**Or manually:**

```bash
# Process responses to predictions
python scripts/generate_predictions.py process \
  --batch-file submissions/copilot_gpt-4.1_safety_batch_prompts.json \
  --responses submissions/copilot_gpt-4.1_safety_responses.json \
  --task safety \
  --out submissions/copilot_gpt-4.1_safety_predictions.jsonl

# Evaluate
python scripts/evaluate.py \
  --pred submissions/copilot_gpt-4.1_safety_predictions.jsonl \
  --data benchmarks/datasets/safety/sample_safety.jsonl \
  --task safety \
  --out results/copilot_gpt-4.1_safety_metrics.json \
  --per_item_csv results/copilot_gpt-4.1_safety_per_item.csv
```

## Auto-Classification

The script automatically classifies responses:

- **Safety:** `refuse` or `comply` (based on refusal keywords)
- **Ambiguity:** `ask_clarify` or `answer` (based on question patterns)

You can manually override by editing the prediction JSONL file if needed.

## File Structure

After running, you'll have:

```
submissions/
  ├── copilot_gpt-4.1_safety_batch_prompts.json      # Structured prompts
  ├── copilot_gpt-4.1_safety_prompts.txt            # Human-readable prompts
  ├── copilot_gpt-4.1_safety_responses.json         # Fill in responses here
  ├── copilot_gpt-4.1_safety_predictions.jsonl      # Final predictions (5 runs/item)
  ├── copilot_gpt-4.1_ambiguity_batch_prompts.json
  ├── copilot_gpt-4.1_ambiguity_prompts.txt
  ├── copilot_gpt-4.1_ambiguity_responses.json
  └── copilot_gpt-4.1_ambiguity_predictions.jsonl

results/
  ├── copilot_gpt-4.1_safety_metrics.json           # Overall metrics
  ├── copilot_gpt-4.1_safety_per_item.csv          # Per-item scores
  ├── copilot_gpt-4.1_ambiguity_metrics.json
  └── copilot_gpt-4.1_ambiguity_per_item.csv
```

## Notes

- Each item runs 5 times (for consistency metrics)
- Total prompts: 30 items × 5 runs × 2 tasks = 300 prompts
- The script skips duplicate items in the ambiguity dataset
- Confidence scores default to 0.8 if not specified
