"""Batch clean all transcripts using Claude."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

import anthropic

# Import the cleanup prompt from config
sys.path.insert(0, str(Path(__file__).parent))
from config.settings import CLEANUP_SYSTEM_PROMPT, ANTHROPIC_API_KEY

TRANSCRIPTS_DIR = Path(__file__).parent / "transcripts"
CLEANED_DIR = Path(__file__).parent / "cleaned_scripts"
CLEANED_DIR.mkdir(exist_ok=True)


def cleanup_transcript(text: str) -> str:
    """Send transcript to Claude for cleanup."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8192,
        system=CLEANUP_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"Clean up this transcript:\n\n{text}"}
        ],
    )
    return message.content[0].text


def main():
    transcripts = sorted(TRANSCRIPTS_DIR.glob("*_transcript.txt"))

    if not transcripts:
        print(f"No transcripts found in {TRANSCRIPTS_DIR}")
        return

    if not ANTHROPIC_API_KEY:
        print("ERROR: Set ANTHROPIC_API_KEY in .env file")
        print("Get your key at: https://console.anthropic.com/settings/keys")
        return

    print(f"Found {len(transcripts)} transcripts")
    print(f"Cleaning with Claude...\n")

    cleaned = 0
    skipped = 0
    errors = 0

    for i, f in enumerate(transcripts, 1):
        output_name = f.stem.replace("_transcript", "_cleaned") + ".txt"
        output_path = CLEANED_DIR / output_name

        if output_path.exists():
            print(f"[{i}/{len(transcripts)}] {f.name} -- already cleaned, skipping")
            skipped += 1
            continue

        text = f.read_text(encoding="utf-8").strip()
        if len(text) < 20:
            print(f"[{i}/{len(transcripts)}] {f.name} -- too short ({len(text)} chars), skipping")
            skipped += 1
            continue

        print(f"[{i}/{len(transcripts)}] {f.name} ({len(text)} chars)...", end=" ", flush=True)

        try:
            cleaned_text = cleanup_transcript(text)
            output_path.write_text(cleaned_text, encoding="utf-8")
            reduction = (1 - len(cleaned_text) / len(text)) * 100
            print(f"done ({len(cleaned_text)} chars, {reduction:.0f}% reduction)")
            cleaned += 1
        except Exception as e:
            print(f"ERROR: {e}")
            errors += 1

    print(f"\nDone! Cleaned: {cleaned}, Skipped: {skipped}, Errors: {errors}")
    print(f"Output: {CLEANED_DIR}")


if __name__ == "__main__":
    main()
