"""Step 3: Synthesize speech from script using ElevenLabs voice clone."""

from pathlib import Path
from elevenlabs import ElevenLabs

from config.settings import (
    ELEVENLABS_API_KEY,
    ELEVENLABS_VOICE_ID,
    ELEVENLABS_MODEL,
    ELEVENLABS_STABILITY,
    ELEVENLABS_SIMILARITY,
    VOICE_OUTPUT_DIR,
)


def synthesize_voice(script_path: str | Path) -> Path:
    """Convert a cleaned script to speech using your ElevenLabs voice clone.

    Returns the path to the saved audio file.
    """
    script_path = Path(script_path)
    script_text = script_path.read_text(encoding="utf-8")

    # Add pauses between paragraphs for natural pacing
    # Double newlines = paragraph break = 1.5 second pause
    import re
    script_text = script_text.replace("[PAUSE]", "... ... ...")
    # Replace paragraph breaks with long pauses
    script_text = re.sub(r'\n\s*\n', '\n... ... ...\n', script_text)
    # Ensure sentence endings have breathing room
    script_text = re.sub(r'\.(\s)', '. ... \\1', script_text)

    print(f"[Voice] Generating audio with ElevenLabs voice clone...")
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

    audio_generator = client.text_to_speech.convert(
        voice_id=ELEVENLABS_VOICE_ID,
        text=script_text,
        model_id=ELEVENLABS_MODEL,
        voice_settings={
            "stability": ELEVENLABS_STABILITY,
            "similarity_boost": ELEVENLABS_SIMILARITY,
        },
    )

    output_path = VOICE_OUTPUT_DIR / f"{script_path.stem.replace('_script', '')}_voice.mp3"

    # audio_generator yields chunks
    with open(output_path, "wb") as f:
        for chunk in audio_generator:
            f.write(chunk)

    print(f"[Voice] Saved synthesized audio to {output_path.name}")
    return output_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m steps.voice_synth <script_file>")
        sys.exit(1)
    result = synthesize_voice(sys.argv[1])
    print(f"Voice audio saved: {result}")
