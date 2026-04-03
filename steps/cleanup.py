"""Step 2: Clean up raw transcript into a polished script using Claude."""

from pathlib import Path
import anthropic

from config.settings import ANTHROPIC_API_KEY, CLEANUP_SYSTEM_PROMPT, CLEANED_SCRIPTS_DIR


def cleanup_script(transcript_path: str | Path) -> Path:
    """Clean up a raw transcript into a polished script.

    Returns the path to the saved cleaned script.
    """
    transcript_path = Path(transcript_path)
    raw_text = transcript_path.read_text(encoding="utf-8")

    print(f"[Cleanup] Sending transcript to Claude for cleanup...")
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=CLEANUP_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"Clean up this transcript:\n\n{raw_text}"}
        ],
    )

    cleaned_text = message.content[0].text

    output_path = CLEANED_SCRIPTS_DIR / f"{transcript_path.stem.replace('_transcript', '')}_script.txt"
    output_path.write_text(cleaned_text, encoding="utf-8")
    print(f"[Cleanup] Saved cleaned script to {output_path.name}")
    return output_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m steps.cleanup <transcript_file>")
        sys.exit(1)
    result = cleanup_script(sys.argv[1])
    print(f"Cleaned script saved: {result}")
