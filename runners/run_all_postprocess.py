# runners/run_all_postprocess.py

import subprocess
import asyncio

from analysis.generate_benchmark_summary import generate_summary


def run(cmd):
    print(f"\n▶ {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def main():
    print("🚀 Running TrustBench post-processing pipeline")

    # -------------------------
    # Core post-processing
    # -------------------------
    run(["python3", "-m", "runners.aggregate_results"])
    run(["python3", "-m", "runners.run_consistency"])
    run(["python3", "-m", "analysis.confidence_calibration"])
    run(["python3", "-m", "analysis.plot_calibration"])
    run(["python3", "-m", "leaderboard.build_leaderboard"])

    # -------------------------
    # NEW: LLM Benchmark Summary
    # -------------------------
    print("\n🧠 Generating LLM benchmark summary")

    try:
        summary = asyncio.run(generate_summary())
        print("✔ Benchmark summary generated")
    except Exception as e:
        # Never fail pipeline because of summary
        print(f"⚠️ Summary generation skipped: {e}")

    print("\n✔ Done")


if __name__ == "__main__":
    main()
