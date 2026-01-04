import os
import json
import pandas as pd
import streamlit as st
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

st.set_page_config(
    page_title="TrustBench Dashboard",
    layout="wide"
)

def best_model_per_task(df, task):
    metric = f"{task}_desired_behavior_rate"
    if metric not in df.columns:
        return None
    return df.sort_values(metric, ascending=False).iloc[0]["model"]

RESULTS = "results"
LEADERBOARD = "leaderboard/leaderboard.csv"
LEADERBOARD_JSON = "leaderboard/leaderboard.json"
AI_SUMMARY_MD = "results/benchmark_summary.md"

# -------------------------
# Leaderboard
# -------------------------
st.title("🏆 TrustBench Leaderboard")

df_lb = pd.read_csv(LEADERBOARD)
st.dataframe(df_lb, width="stretch")

# -------------------------
# Model selector
# -------------------------
models = sorted(df_lb["model"].tolist())
model = st.selectbox("Select model", models)

# -------------------------
# Task selector
# -------------------------
task = st.selectbox("Task", ["safety", "ambiguity", "reasoning"])

model_dir = f"{RESULTS}/{model}"
plot_path = f"{RESULTS}/{model}/plots/{task}_calibration.png"

if os.path.exists(plot_path):
    st.image(plot_path)

# -------------------------
# Metrics
# -------------------------
st.subheader("📊 Task Metrics")

metrics_path = f"{model_dir}/{task}_metrics.json"
if os.path.exists(metrics_path):
    with open(metrics_path) as f:
        metrics = json.load(f)

    pretty_metrics = {
        "Desired behavior rate": metrics.get("desired_behavior_rate"),
        "Run stability": metrics.get("run_stability"),
        "Blocked response rate": metrics.get("blocked_rate"),
        "Confidence (mean)": metrics.get("confidence_mean"),
        "Confidence (std)": metrics.get("confidence_std"),
    }

    if metrics.get("safety_refusal_rate") is not None:
        pretty_metrics["Safety refusal rate"] = metrics.get("safety_refusal_rate")

    st.table(
        [{"Metric": k, "Value": v} for k, v in pretty_metrics.items() if v is not None]
    )
else:
    st.warning("Metrics not found")

# -------------------------
# Run-to-run consistency
# -------------------------
st.subheader("🔁 Run Stability")

cons_path = f"{model_dir}/{task}_consistency.json"
if os.path.exists(cons_path):
    with open(cons_path) as f:
        cons = json.load(f)
    st.metric("Run stability", round(cons["consistency"], 3))
else:
    st.warning("Consistency data not found")

# -------------------------
# Calibration curve
# -------------------------
st.subheader("📈 Confidence vs Outcome Frequency")

cal_path = f"{model_dir}/{task}_calibration.json"
if os.path.exists(cal_path):
    with open(cal_path) as f:
        cal = json.load(f)

    df_cal = pd.DataFrame(cal["bins"])

    # backward compatibility
    y_col = (
        "outcome_frequency"
        if "outcome_frequency" in df_cal.columns
        else "consistency_rate"
    )

    st.line_chart(
        df_cal.set_index("confidence_bin")[[y_col]],
        height=300
    )
else:
    st.warning("Calibration data not found")


# -------------------------
# CSV downloads
# -------------------------
st.subheader("📤 Downloads")

csv_dir = f"{model_dir}/csv"
if os.path.exists(csv_dir):
    for f in os.listdir(csv_dir):
        if f.startswith(task):
            with open(f"{csv_dir}/{f}") as fh:
                st.download_button(
                    label=f"Download {f}",
                    data=fh.read(),
                    file_name=f
                )

# ============================================================
# 🔽 🔽 🔽 NEW ADDITIONS (ONLY ADDITIVE) 🔽 🔽 🔽
# ============================================================

st.divider()

# -------------------------
# Run-level exploration
# -------------------------
st.subheader("🎯 Run-level Exploration")

sub_path = f"submissions/{model}/{task}.jsonl"
if os.path.exists(sub_path):
    df_runs = pd.read_json(sub_path, lines=True)

    runs = sorted(df_runs["run_id"].unique())
    run_filter = st.multiselect("Filter by run_id", runs, default=runs)

    df_filtered = df_runs[df_runs["run_id"].isin(run_filter)]
    st.dataframe(df_filtered, width="stretch")
else:
    st.info("Run-level data not available.")

# -------------------------
# Confidence distribution
# -------------------------
st.subheader("📊 Confidence Distribution")

if "confidence" in df_filtered.columns:
    st.bar_chart(df_filtered["confidence"].value_counts().sort_index())

# -------------------------
# Consistency across tasks
# -------------------------
st.subheader("🔁 Run Stability Across Tasks")

rows = []
for t in ["safety", "ambiguity", "reasoning"]:
    p = f"{model_dir}/{t}_consistency.json"
    if os.path.exists(p):
        with open(p) as f:
            c = json.load(f)
        rows.append({"task": t, "run_stability": c["consistency"]})

if rows:
    df_cons = pd.DataFrame(rows).set_index("task")
    st.bar_chart(df_cons)

# ============================================================
# 📊 COMPARATIVE ANALYSIS (NEW)
# ============================================================

st.divider()
st.subheader("📊 Comparative Analysis")

compare_models = st.multiselect(
    "Compare models",
    models,
    default=models[:3]
)

if compare_models:
    df_cmp = df_lb[df_lb["model"].isin(compare_models)]
    st.dataframe(df_cmp, width="stretch")

# ============================================================
# 🧠 AI BENCHMARK SUMMARY (NEW)
# ============================================================

st.divider()
st.subheader("🧠 LLM-written Benchmark Summary")

from analysis.generate_benchmark_summary import (
    generate_summary,
    load_cached_summary,
)
import asyncio

cached = load_cached_summary()

if cached:
    st.markdown(cached)
else:
    if st.button("Generate AI Summary"):
        with st.spinner("Generating benchmark summary..."):
            summary = asyncio.run(generate_summary())
            st.markdown(summary)
st.divider()
st.subheader("📊 Cross-Model Comparison")

task_metric = st.selectbox(
    "Compare models on:",
    [
        "safety_desired_behavior_rate",
        "ambiguity_desired_behavior_rate",
        "reasoning_desired_behavior_rate",
        "safety_run_stability",
        "ambiguity_run_stability",
        "reasoning_run_stability",
    ],
)

if task_metric in df_lb.columns:
    st.bar_chart(
        df_lb.set_index("model")[[task_metric]],
        height=350
    )
else:
    st.warning("Metric not available.")

st.divider()
st.subheader("🥇 Best Model Per Task")

for t in ["safety", "ambiguity", "reasoning"]:
    best = best_model_per_task(df_lb, t)
    if best:
        st.success(f"**{t.capitalize()} winner:** {best}")
# -------------------------
# Debug panel
# -------------------------
with st.expander("🧪 Data Availability (Debug)"):
    st.write("Model directory:", model_dir)
    if os.path.exists(model_dir):
        for root, _, files in os.walk(model_dir):
            for f in files:
                st.write(os.path.join(root, f))
