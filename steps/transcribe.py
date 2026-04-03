"""Step 1: Transcribe audio to text using OpenAI Whisper."""

from pathlib import Path
import whisper

from config.settings import WHISPER_MODEL, TRANSCRIPTS_DIR


def transcribe(audio_path: str | Path) -> Path:
    """Transcribe an audio file and save the text to the transcripts folder.

    Returns the path to the saved transcript file.
    """
    audio_path = Path(audio_path)
    print(f"[Transcribe] Loading Whisper model '{WHISPER_MODEL}'...")
    model = whisper.load_model(WHISPER_MODEL)

    print(f"[Transcribe] Transcribing {audio_path.name}...")
    result = model.transcribe(str(audio_path))
    text = result["text"].strip()

    output_path = TRANSCRIPTS_DIR / f"{audio_path.stem}_transcript.txt"
    output_path.write_text(text, encoding="utf-8")
    print(f"[Transcribe] Saved transcript to {output_path.name}")
    return output_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m steps.transcribe <audio_file>")
        sys.exit(1)
    result = transcribe(sys.argv[1])
    print(f"Transcript saved: {result}")
