# TrustBench Platform

TrustBench is a reproducible evaluation framework for benchmarking LLMs across
**safety**, **ambiguity handling**, and **reasoning**, with confidence calibration
and run-to-run consistency analysis.

---

## 📂 Project Structure

benchmarks/ # JSONL datasets
llm/ # LLM provider clients (xAI, OpenAI, etc.)
normalize/ # Prediction normalization logic
confidence/ # Confidence scoring
sampling/ # Deterministic sampling
utils/ # Writers and helpers

runners/
├─ auto_run_async.py # Calls models (API)
├─ aggregate_results.py # Aggregates raw outputs
├─ run_consistency.py # Run-to-run consistency

analysis/
├─ confidence_calibration.py # Calibration bins
├─ plot_calibration.py # Calibration plots
├─ baseline_deltas.py # Baseline comparison

leaderboard/
├─ build_leaderboard.py
├─ leaderboard.csv
└─ artifacts/

results/ # Metrics, CSVs, plots
submissions/ # Raw model outputs (JSONL)
app.py # Streamlit dashboard

---

## 🔑 Environment Setup

Create a `.env` file:

OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
XAI_API_KEY=xai-...

Install dependencies:

pip install -r requirements.txt


---

## 🚀 Full Execution Pipeline

### Step 1: Run model inference (API calls)

python3 -m runners.auto_run_async


> This is the **only step that touches an LLM API**.

---

### Step 2: Aggregate results

python3 -m runners.aggregate_results


---

### Step 3: Run consistency analysis

python3 -m runners.run_consistency


---

### Step 4: Confidence calibration

python3 -m analysis.confidence_calibration


---

### Step 5: Generate calibration plots

python3 -m analysis.plot_calibration


---

### Step 6: Build leaderboard

python3 -m leaderboard.build_leaderboard


---

### Step 7: Baseline deltas

python3 -m analysis.baseline_deltas


---

### Step 8: Launch UI

streamlit run app.py


---

## 📊 Metrics Produced

- Exact accuracy
- Safety refusal rate
- Ambiguity clarification rate
- Reasoning accuracy
- Confidence calibration
- Run-to-run consistency
- Baseline deltas

All metrics are exported as **CSV and JSON**.

---

## 🧪 Reproducibility Guarantees

- Fixed random seeds
- Deterministic sampling
- Raw JSONL outputs preserved
- Offline evaluation after inference

---

## 📄 License

MIT