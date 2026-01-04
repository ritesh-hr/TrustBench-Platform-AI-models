#!/usr/bin/env python3
"""
Interactive prompt collector for Cursor chat.
Shows prompts one at a time and collects responses.
"""

import json
import argparse
import re
from pathlib import Path


def load_batch_file(batch_file: str):
    """Load the batch prompts file."""
    with open(batch_file, "r", encoding="utf-8") as f:
        return json.load(f)


def load_responses_file(responses_file: str):
    """Load existing responses file."""
    try:
        with open(responses_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_responses_file(responses_file: str, responses: dict):
    """Save responses file."""
    with open(responses_file, "w", encoding="utf-8") as f:
        json.dump(responses, f, indent=2)


def extract_confidence_from_response(response: str) -> float:
    """
    Extract confidence score from response text.
    Looks for patterns like:
    - "Confidence: 0.95"
    - "confidence: 0.8"
    - "Confidence level: 0.9"
    - "I am 95% confident" -> 0.95
    - Numbers between 0 and 1 at the end
    """
    if not response:
        return 0.8
    
    response_lower = response.lower()
    
    # Pattern 1: "Confidence: 0.95" or "confidence: 0.8"
    patterns = [
        r'confidence\s*:?\s*(\d+\.?\d*)',
        r'confidence\s+level\s*:?\s*(\d+\.?\d*)',
        r'conf\s*:?\s*(\d+\.?\d*)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, response_lower)
        if match:
            try:
                conf = float(match.group(1))
                # If it's a percentage (0-100), convert to 0-1
                if conf > 1.0:
                    conf = conf / 100.0
                return max(0.0, min(1.0, conf))
            except ValueError:
                continue
    
    # Pattern 2: "I am X% confident" -> extract percentage
    percent_match = re.search(r'(\d+)%\s+confident', response_lower)
    if percent_match:
        try:
            conf = float(percent_match.group(1)) / 100.0
            return max(0.0, min(1.0, conf))
        except ValueError:
            pass
    
    # Pattern 3: Look for decimal numbers between 0 and 1 near the end
    # (last 100 characters)
    end_text = response[-100:] if len(response) > 100 else response
    decimal_matches = re.findall(r'\b(0?\.\d+|\d+\.\d+)\b', end_text)
    for match in reversed(decimal_matches):  # Check from end
        try:
            conf = float(match)
            if 0.0 <= conf <= 1.0:
                return conf
        except ValueError:
            continue
    
    # Default if nothing found
    return 0.8


def interactive_collect(batch_file: str, responses_file: str):
    """Interactive prompt collection."""
    batch_data = load_batch_file(batch_file)
    responses = load_responses_file(responses_file)
    
    prompts = batch_data["prompts"]
    total = len(prompts)
    completed = sum(1 for p in prompts if f"{p['item_id']}_{p['run_id']}" in responses and responses[f"{p['item_id']}_{p['run_id']}"].get("response", "").strip())
    
    print("=" * 80)
    print("Interactive Prompt Collector")
    print(f"Task: {batch_data['task']}")
    print(f"Model: {batch_data['model']}")
    print(f"Progress: {completed}/{total} completed")
    print("=" * 80)
    print("\nInstructions:")
    print("1. Copy the prompt below")
    print("2. Paste into Cursor chat (select GPT-4.1)")
    print("3. Copy the model's response")
    print("4. Paste it here when prompted")
    print("5. Press Enter to continue (or 'q' to quit, 's' to skip)")
    print("\n" + "=" * 80 + "\n")
    
    for i, prompt_info in enumerate(prompts, 1):
        item_id = prompt_info["item_id"]
        run_id = prompt_info["run_id"]
        key = f"{item_id}_{run_id}"
        
        # Skip if already completed
        if key in responses and responses[key].get("response", "").strip():
            continue
        
        print(f"\n{'='*80}")
        print(f"PROMPT {i}/{total}")
        print(f"ID: {item_id} | Run: {run_id} | Expected: {prompt_info['expected']}")
        print(f"{'='*80}\n")
        
        # Show the prompt in a copy-friendly format (single block for Cursor chat)
        print("COPY THIS PROMPT (paste directly into Cursor chat):")
        print("-" * 80)
        print(prompt_info['full_prompt'])
        print("-" * 80)
        print("\nAfter getting the response from Cursor chat, paste it below:")
        
        response = input("\nResponse (or 'q' to quit, 's' to skip, Enter to use empty): ").strip()
        
        if response.lower() == 'q':
            print("\nSaving progress and quitting...")
            save_responses_file(responses_file, responses)
            return
        elif response.lower() == 's':
            print("Skipped.")
            continue
        
        # Auto-extract confidence from response
        confidence = extract_confidence_from_response(response)
        
        # Show extracted confidence and allow override
        print(f"\n✓ Extracted confidence: {confidence:.2f}")
        conf_input = input("Press Enter to use this, or type a different value (0-1): ").strip()
        
        if conf_input:
            try:
                confidence = float(conf_input)
                confidence = max(0.0, min(1.0, confidence))
                print(f"✓ Using confidence: {confidence:.2f}")
            except ValueError:
                print(f"⚠ Invalid input, using extracted: {confidence:.2f}")
        
        # Save response
        responses[key] = {
            "response": response,
            "confidence": confidence
        }
        
        # Auto-save after each response
        save_responses_file(responses_file, responses)
        
        completed = sum(1 for p in prompts if f"{p['item_id']}_{p['run_id']}" in responses and responses[f"{p['item_id']}_{p['run_id']}"].get("response", "").strip())
        print(f"✓ Saved! Progress: {completed}/{total}")
    
    print(f"\n{'='*80}")
    print(f"✓ All prompts completed! ({completed}/{total})")
    print(f"✓ Responses saved to: {responses_file}")
    print(f"{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Interactive prompt collector for Cursor chat"
    )
    parser.add_argument(
        "--batch-file",
        required=True,
        help="Batch prompts JSON file"
    )
    parser.add_argument(
        "--responses",
        required=True,
        help="Responses JSON file to update"
    )
    
    args = parser.parse_args()
    interactive_collect(args.batch_file, args.responses)


if __name__ == "__main__":
    main()
