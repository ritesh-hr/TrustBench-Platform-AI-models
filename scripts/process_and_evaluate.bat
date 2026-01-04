@echo off
REM Process responses and evaluate predictions
REM Usage: scripts\process_and_evaluate.bat copilot_gpt-4.1 safety

set MODEL_NAME=%1
if "%MODEL_NAME%"=="" set MODEL_NAME=copilot_gpt-4.1
set TASK=%2
if "%TASK%"=="" set TASK=safety

echo ==========================================
echo Processing and evaluating: %MODEL_NAME% - %TASK%
echo ==========================================
echo.

REM Process responses to predictions
python scripts\generate_predictions.py process ^
  --batch-file submissions\%MODEL_NAME%_%TASK%_batch_prompts.json ^
  --responses submissions\%MODEL_NAME%_%TASK%_responses.json ^
  --task %TASK% ^
  --out submissions\%MODEL_NAME%_%TASK%_predictions.jsonl

REM Evaluate
if "%TASK%"=="safety" (
    set DATA_FILE=benchmarks\datasets\safety\sample_safety.jsonl
) else if "%TASK%"=="ambiguity" (
    set DATA_FILE=benchmarks\datasets\ambiguity\sample_ambiguity.jsonl
) else (
    echo Unknown task: %TASK%
    exit /b 1
)

python scripts\evaluate.py ^
  --pred submissions\%MODEL_NAME%_%TASK%_predictions.jsonl ^
  --data %DATA_FILE% ^
  --task %TASK% ^
  --out results\%MODEL_NAME%_%TASK%_metrics.json ^
  --per_item_csv results\%MODEL_NAME%_%TASK%_per_item.csv

echo.
echo ==========================================
echo Processing and evaluation complete!
echo ==========================================
