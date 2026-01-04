#!/bin/bash
# Process responses and evaluate predictions
# Usage: bash scripts/process_and_evaluate.sh copilot_gpt-4.1 safety

MODEL_NAME=${1:-copilot_gpt-4.1}
TASK=${2:-safety}

echo "=========================================="
echo "Processing and evaluating: $MODEL_NAME - $TASK"
echo "=========================================="
echo ""

# Process responses to predictions
python scripts/generate_predictions.py process \
  --batch-file submissions/${MODEL_NAME}_${TASK}_batch_prompts.json \
  --responses submissions/${MODEL_NAME}_${TASK}_responses.json \
  --task $TASK \
  --out submissions/${MODEL_NAME}_${TASK}_predictions.jsonl

# Evaluate
if [ "$TASK" == "safety" ]; then
    DATA_FILE="benchmarks/datasets/safety/sample_safety.jsonl"
elif [ "$TASK" == "ambiguity" ]; then
    DATA_FILE="benchmarks/datasets/ambiguity/sample_ambiguity.jsonl"
else
    echo "Unknown task: $TASK"
    exit 1
fi

python scripts/evaluate.py \
  --pred submissions/${MODEL_NAME}_${TASK}_predictions.jsonl \
  --data $DATA_FILE \
  --task $TASK \
  --out results/${MODEL_NAME}_${TASK}_metrics.json \
  --per_item_csv results/${MODEL_NAME}_${TASK}_per_item.csv

echo ""
echo "=========================================="
echo "✓ Processing and evaluation complete!"
echo "=========================================="
