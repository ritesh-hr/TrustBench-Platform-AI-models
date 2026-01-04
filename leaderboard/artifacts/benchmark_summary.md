# Benchmark Leaderboard Insights

## 🥇 Best Model per Task
- **Ambiguity**: `openai_gpt41` with the lowest confidence standard deviation (0.0671).
- **Reasoning**: `openai_gpt41` leading with the lowest confidence standard deviation (0.03).
- **Safety**: `openai_gpt41` with zero safety confidence standard deviation (0).

## ⚖️ Strengths and Weaknesses
- **Strengths**:
  - `openai_gpt41` excels in stability and low variability across ambiguity, reasoning, and safety tasks.
  - `google_gemini_25_pro` shows strong safety performance with a refusal rate of 0.
- **Weaknesses**:
  - `xai_grok_4_1_fast_reasoning` has the highest ambiguity confidence standard deviation (0.1536).
  - `openai_gpt5` displays high variability in reasoning (0.1675).

## 🔁 Stability vs Confidence Observations
- `openai_gpt41` consistently shows low confidence standard deviations across all tasks, indicating stable performance.
- Higher variability in models like `xai_grok_4_1_fast_reasoning` suggests instability in ambiguous situations.

## 🚨 Notable Anomalies
- All desired behavior rates and run stability metrics are marked as `nan`, indicating missing data for proper evaluation.
- `claude-sonnet-4-5` and similar models have a safety refusal rate of 1, contrasting starkly with models like `google_gemini_25_pro` with a rate of 0.