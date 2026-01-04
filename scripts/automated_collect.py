#!/usr/bin/env python3
"""
Automated prompt collector with clipboard integration for Cursor chat.
Automatically copies prompts to clipboard for faster workflow.
"""

import json
import argparse
import re
import sys
from pathlib import Path

# Try to import clipboard library
try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
    CLIPBOARD_TYPE = 'pyperclip'
except ImportError:
    try:
        import win32clipboard
        CLIPBOARD_AVAILABLE = True
        CLIPBOARD_TYPE = 'win32'
    except ImportError:
        CLIPBOARD_AVAILABLE = False
        print("[WARNING] Clipboard library not found. Install with: pip install pyperclip")
        print("          Or: pip install pywin32")


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


def copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard."""
    if not CLIPBOARD_AVAILABLE:
        return False
    
    try:
        if CLIPBOARD_TYPE == 'pyperclip':
            pyperclip.copy(text)
            return True
        elif CLIPBOARD_TYPE == 'win32':
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text)
            win32clipboard.CloseClipboard()
            return True
    except Exception as e:
        print(f"[WARNING] Failed to copy to clipboard: {e}")
        return False
    
    return False


def extract_confidence_from_response(response: str) -> float:
    """Extract confidence score from response text."""
    if not response:
        return 0.8
    
    response_lower = response.lower()
    
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
                if conf > 1.0:
                    conf = conf / 100.0
                return max(0.0, min(1.0, conf))
            except ValueError:
                continue
    
    percent_match = re.search(r'(\d+)%\s+confident', response_lower)
    if percent_match:
        try:
            conf = float(percent_match.group(1)) / 100.0
            return max(0.0, min(1.0, conf))
        except ValueError:
            pass
    
    end_text = response[-100:] if len(response) > 100 else response
    decimal_matches = re.findall(r'\b(0?\.\d+|\d+\.\d+)\b', end_text)
    for match in reversed(decimal_matches):
        try:
            conf = float(match)
            if 0.0 <= conf <= 1.0:
                return conf
        except ValueError:
            continue
    
    return 0.8


def automated_collect(batch_file: str, responses_file: str):
    """Automated prompt collection with clipboard integration."""
    batch_data = load_batch_file(batch_file)
    responses = load_responses_file(responses_file)
    
    prompts = batch_data["prompts"]
    total = len(prompts)
    completed = sum(1 for p in prompts if f"{p['item_id']}_{p['run_id']}" in responses and responses[f"{p['item_id']}_{p['run_id']}"].get("response", "").strip())
    
    print("=" * 80)
    print("Automated Prompt Collector with Clipboard Integration")
    print(f"Task: {batch_data['task']}")
    print(f"Model: {batch_data['model']}")
    print(f"Progress: {completed}/{total} completed")
    if CLIPBOARD_AVAILABLE:
        print("[OK] Clipboard automation enabled - prompts will auto-copy!")
    else:
        print("[WARNING] Clipboard not available - manual copy required")
    print("=" * 80)
    print("\nWorkflow:")
    print("1. Prompt is automatically copied to clipboard")
    print("2. Switch to Cursor chat and paste (Ctrl+V)")
    print("3. Get the model's response")
    print("4. Copy the response and paste it here")
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
        
        prompt_text = prompt_info['full_prompt']
        
        # Automatically copy to clipboard
        if CLIPBOARD_AVAILABLE:
            if copy_to_clipboard(prompt_text):
                print("[OK] Prompt copied to clipboard automatically!")
                print("\nPrompt (already in clipboard, ready to paste in Cursor):")
            else:
                print("[WARNING] Failed to copy - please copy manually:")
        else:
            print("COPY THIS PROMPT:")
        
        print("-" * 80)
        print(prompt_text)
        print("-" * 80)
        
        if CLIPBOARD_AVAILABLE:
            print("\n>>> Prompt is in your clipboard! Switch to Cursor and paste (Ctrl+V) <<<")
        
        print("\n" + "="*80)
        print("COLLECTING RESPONSE:")
        print("="*80)
        print("After getting the response from Cursor chat:")
        print("1. Select ALL the text in the response (triple-click or Ctrl+A)")
        print("2. Copy it (Ctrl+C)")
        print("3. Paste it below (Ctrl+V)")
        print("\nIMPORTANT: Paste the ENTIRE response, then press Enter TWICE to finish")
        print("Or type 'END' on a new line after pasting")
        print("="*80)
        
        # For multi-line input, read until user enters END or two empty lines
        print("\nPaste the response below (then press Enter twice, or type 'END'):")
        response_lines = []
        empty_count = 0
        
        while True:
            try:
                line = input()
                # Check for quit/skip commands first
                if line.strip().upper() == 'Q':
                    print("\nSaving progress and quitting...")
                    save_responses_file(responses_file, responses)
                    return
                elif line.strip().upper() == 'S':
                    print("Skipped.")
                    response = ""
                    break
                elif line.strip().upper() == 'END':
                    break
                
                # Track empty lines
                if not line.strip():
                    empty_count += 1
                    if empty_count >= 2 and response_lines:
                        # Two consecutive empty lines after content = done
                        break
                else:
                    empty_count = 0
                    response_lines.append(line)
            except EOFError:
                break
        
        response = '\n'.join(response_lines).strip()
        
        if not response:
            print("\nSaving progress and quitting...")
            save_responses_file(responses_file, responses)
            return
        elif response.lower() == 's':
            print("Skipped.")
            continue
        
        # Auto-extract confidence from response
        confidence = extract_confidence_from_response(response)
        
        # Show extracted confidence and allow override
        print(f"\n[OK] Extracted confidence: {confidence:.2f}")
        conf_input = input("Press Enter to use this, or type a different value (0-1): ").strip()
        
        if conf_input:
            try:
                confidence = float(conf_input)
                confidence = max(0.0, min(1.0, confidence))
                print(f"[OK] Using confidence: {confidence:.2f}")
            except ValueError:
                print(f"[WARNING] Invalid input, using extracted: {confidence:.2f}")
        else:
            print(f"[OK] Using extracted confidence: {confidence:.2f}")
        
        # Save response
        responses[key] = {
            "response": response,
            "confidence": confidence
        }
        
        # Auto-save after each response
        save_responses_file(responses_file, responses)
        
        completed = sum(1 for p in prompts if f"{p['item_id']}_{p['run_id']}" in responses and responses[f"{p['item_id']}_{p['run_id']}"].get("response", "").strip())
        print(f"[OK] Saved! Progress: {completed}/{total}")
    
    print(f"\n{'='*80}")
    print(f"[OK] All prompts completed! ({completed}/{total})")
    print(f"[OK] Responses saved to: {responses_file}")
    print(f"{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Automated prompt collector with clipboard integration for Cursor chat"
    )
    parser.add_argument(
        "model",
        help="Model name (e.g., claude_sonnet-4.5, copilot_gpt-4.1)"
    )
    parser.add_argument(
        "task",
        choices=["safety", "ambiguity", "reasoning"],
        help="Task name"
    )
    parser.add_argument(
        "--batch-file",
        help="Batch prompts JSON file (auto-generated if not provided)"
    )
    parser.add_argument(
        "--responses",
        help="Responses JSON file (auto-generated if not provided)"
    )
    
    args = parser.parse_args()
    
    # Auto-generate file paths if not provided
    if not args.batch_file:
        args.batch_file = f"submissions/{args.model}_{args.task}_batch_prompts.json"
    if not args.responses:
        args.responses = f"submissions/{args.model}_{args.task}_responses.json"
    
    automated_collect(args.batch_file, args.responses)


if __name__ == "__main__":
    main()
