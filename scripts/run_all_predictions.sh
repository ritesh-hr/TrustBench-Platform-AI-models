#!/bin/bash
# Quick script to generate all prompts and templates for safety and ambiguity tasks
# Usage: bash scripts/run_all_predictions.sh copilot_gpt-4.1

MODEL_NAME=${1:-copilot_gpt-4.1}
NUM_RUNS=5

echo "=========================================="
echo "Generating predictions for: $MODEL_NAME"
echo "Runs per item: $NUM_RUNS"
echo "=========================================="
echo ""

# Safety task
echo "--- SAFETY TASK ---"
python scripts/generate_predictions.py generate \
  --data benchmarks/datasets/safety/sample_safety.jsonl \
  --task safety \
  --model $MODEL_NAME \
  --runs $NUM_RUNS

python scripts/generate_predictions.py template \
  --batch-file submissions/${MODEL_NAME}_safety_batch_prompts.json \
  --out submissions/${MODEL_NAME}_safety_responses.json

echo ""
echo "--- AMBIGUITY TASK ---"
python scripts/generate_predictions.py generate \
  --data benchmarks/datasets/ambiguity/sample_ambiguity.jsonl \
  --task ambiguity \
  --model $MODEL_NAME \
  --runs $NUM_RUNS

python scripts/generate_predictions.py template \
  --batch-file submissions/${MODEL_NAME}_ambiguity_batch_prompts.json \
  --out submissions/${MODEL_NAME}_ambiguity_responses.json

echo ""
echo "=========================================="
echo "✓ All prompts and templates generated!"
echo ""
echo "Next steps:"
echo "1. Open the .txt files in submissions/ to see formatted prompts"
echo "2. Use Cursor chat to get responses for each prompt"
echo "3. Fill in the responses JSON files"
echo "4. Run the process commands to generate predictions"
echo "=========================================="
