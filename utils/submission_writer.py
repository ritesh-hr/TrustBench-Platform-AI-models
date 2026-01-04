# utils/submission_writer.py
import os
import json

BASE_DIR = "submissions"

def write(model_id: str, task: str, record: dict):
    model_dir = os.path.join(BASE_DIR, model_id)
    os.makedirs(model_dir, exist_ok=True)

    path = os.path.join(model_dir, f"{task}.jsonl")

    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
