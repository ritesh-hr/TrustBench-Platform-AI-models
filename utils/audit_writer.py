import json, os

def write_audit(model_dir, task, record):
    audit_dir = f"audit/{model_dir}"
    os.makedirs(audit_dir, exist_ok=True)
    path = f"{audit_dir}/{task}.jsonl"

    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
