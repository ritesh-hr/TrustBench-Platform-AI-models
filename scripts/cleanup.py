import os

FILES = [
    
    "leaderboard/leaderboard.csv",
    "leaderboard/leaderboard.json",

    ".env",

    "audits/claude-sonnet-4-5/ambiguity.jsonl",
    "audits/claude-sonnet-4-5/reasoning.jsonl",
    "audits/claude-sonnet-4-5/safety.jsonl",

    "audits/google_gemini_25_pro/ambiguity.jsonl",
    "audits/google_gemini_25_pro/reasoning.jsonl",
    "audits/google_gemini_25_pro/safety.jsonl",

    "audits/google_gemini_3_pro_preview/ambiguity.jsonl",
    "audits/google_gemini_3_pro_preview/reasoning.jsonl",
    "audits/google_gemini_3_pro_preview/safety.jsonl",

    "audits/openai_gpt41/ambiguity.jsonl",
    "audits/openai_gpt41/reasoning.jsonl",
    "audits/openai_gpt41/safety.jsonl",

    "audits/openai_gpt4o/ambiguity.jsonl",
    "audits/openai_gpt4o/reasoning.jsonl",
    "audits/openai_gpt4o/safety.jsonl",

    "audits/openai_gpt5/ambiguity.jsonl",
    "audits/openai_gpt5/reasoning.jsonl",
    "audits/openai_gpt5/safety.jsonl",

    "audits/xai_grok_4_1_fast_reasoning/ambiguity.jsonl",
    "audits/xai_grok_4_1_fast_reasoning/reasoning.jsonl",
    "audits/xai_grok_4_1_fast_reasoning/safety.jsonl",

    

]

RESULTS_DIRS = [
    "results/claude-sonnet-4-5",
    "results/google_gemini_3_pro_preview",
    "results/google_gemini_25_pro",
    "results/openai_gpt4o",
    "results/openai_gpt5",
    "results/openai_gpt41",
    "results/xai_grok_4_1_fast_reasoning",
    "submissions/claude-sonnet-4-5/",
    "submissions/google_gemini_3_pro_preview/",
    "submissions/google_gemini_25_pro/",
    "submissions/openai_gpt4o/",
    "submissions/openai_gpt5/",
    "submissions/openai_gpt41/",
    "submissions/xai_grok_4_1_fast_reasoning/"
]

def delete_files_recursively(root):
    if not os.path.isdir(root):
        return

    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            path = os.path.join(dirpath, name)
            os.remove(path)
            print(f"🗑️ Deleted: {path}")

def main():
    for path in FILES:
        if os.path.isfile(path):
            os.remove(path)
            print(f"🗑️ Deleted: {path}")
        else:
            print(f"⚠️ Missing (skipped): {path}")
    for root in RESULTS_DIRS:
        delete_files_recursively(root)

    print("\n✅ File-only cleanup complete.")

if __name__ == "__main__":
    main()
