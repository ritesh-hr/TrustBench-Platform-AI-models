import asyncio
import json
from dotenv import load_dotenv

from llm.model_registry import MODELS
from llm.dispatcher_async import call_model
from sampling.sampler import sample_questions


from normalize.predictions import (
    safety,
    ambiguity,
    reasoning,
    safety_audit,
    ambiguity_audit,
    reasoning_audit,
)

from confidence.scoring import score
from utils.submission_writer import write
from utils.audit_writer import write_audit


load_dotenv()

# -----------------------
# CONFIG
# -----------------------

RUNS = 5
BASE_SEED = 100
sample_size = 30
OUT = "submissions"

ENABLED_PROVIDERS = {
    "xai",        # Grok
    "openai",     # OpenAI (GPT-4o, GPT-4.1, GPT-5)
    "google",     # Gemini
    "anthropic",  # Claude
}
# ENABLED_PROVIDERS = {"openai"}  
from normalize.predictions import (
    safety, safety_audit,
    ambiguity, ambiguity_audit,
    reasoning, reasoning_audit
)

TASKS = {
    "safety": {
        "file": "benchmarks/datasets/safety/sample_safety.jsonl",
        "normalize": safety,
        "audit": safety_audit,
    },
    "reasoning": {
        "file": "benchmarks/datasets/reasoning/sample_reasoning.jsonl",
        "normalize": reasoning,
        "audit": reasoning_audit,
    },
    "ambiguity": {
        "file": "benchmarks/datasets/ambiguity/sample_ambiguity.jsonl",
        "normalize": ambiguity,
        "audit": ambiguity_audit,
    },
}


# -----------------------
# RUNNER
# -----------------------

async def run_model(model):
    print(f"\n▶ Running model: {model['id']}")
    model_dir = f"{OUT}/{model['id']}"

    for run_idx in range(RUNS):
        run_id = f"r{run_idx + 1}"
        seed = BASE_SEED + run_idx
        print(f"  Run {run_id} (seed={seed})")
        for task, cfg in TASKS.items():
            questions = sample_questions(cfg["file"], sample_size, seed)
            print(f"    Task: {task} ({len(questions)} questions)")

            for q in questions:
                # dataset compatibility
                prompt = q.get("prompt") or q.get("question")
                if not prompt:
                    continue

                # normalize + audit
                raw = await call_model(
                    model["provider"],
                    model["name"],
                    prompt
                )
                

                if raw is None or not isinstance(raw, str) or not raw.strip():
                    print(f"      ⚠️ Empty response (model={model['id']}, task={task}, id={q['id']})")
                    raw = ""
                pred = cfg["normalize"](raw)
                audit_fn = cfg.get("audit")
                audit = audit_fn(raw) if audit_fn else None

                conf, conf_version = score(raw, task)
                # -----------------------
                # SUBMISSION OUTPUT
                # -----------------------
                write(model["id"], task, {
                    "id": q["id"],
                    "task": task,
                    "model": model["id"],
                    "run_id": run_id,
                    "prompt": prompt,
                    "response": raw,
                    "prediction": pred,
                    "confidence": conf,
                    "confidence_version": conf_version
                })

                # -----------------------
                # AUDIT OUTPUT (THIS IS FINE)
                # -----------------------
                write_audit(model["id"], task, {
                    "id": q["id"],
                    "task": task,
                    "model": model["id"],
                    "run_id": run_id,
                    "prompt": prompt,
                    "response": raw,
                    "prediction": pred,
                    "confidence": conf,
                    "rule_triggered": audit
                })

    print(f"✔ Finished model: {model['id']}")

# -----------------------
# MAIN
# -----------------------

async def main():
    selected = [m for m in MODELS if m["provider"] in ENABLED_PROVIDERS]
    await asyncio.gather(*(run_model(m) for m in selected))


if __name__ == "__main__":
    asyncio.run(main())

    import subprocess
    subprocess.run(["python3", "-m", "runners.run_all_postprocess"], check=True)


    print("\n✅ Full TrustBench pipeline finished.\n")

    # cost summary (optional, Grok only)
    try:
        from llm.xai_client import tracker
        with open("leaderboard/artifacts/costs.json", "w") as f:
            json.dump(tracker.summary(), f, indent=2)
    except Exception:
        pass
