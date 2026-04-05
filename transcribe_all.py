"""Transcribe all audio/video files in input_audio/ folder."""

import sys
import os
from pathlib import Path

# Add ffmpeg to PATH if not already there (avoids terminal restart)
ffmpeg_paths = [
    r"C:\Users\nicho\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin",
    r"C:\Users\nicho\AppData\Local\Microsoft\WinGet\Links",
    r"C:\ProgramData\chocolatey\bin",
]
for p in ffmpeg_paths:
    if p not in os.environ["PATH"]:
        os.environ["PATH"] += ";" + p

import whisper

INPUT_DIR = Path(__file__).parent / "input_audio"
OUTPUT_DIR = Path(__file__).parent / "transcripts"
OUTPUT_DIR.mkdir(exist_ok=True)

EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm", ".mp4", ".mov", ".mkv"}
MODEL = "base"  # options: tiny, base, small, medium, large


def main():
    files = [f for f in INPUT_DIR.iterdir() if f.suffix.lower() in EXTENSIONS]

    if not files:
        print(f"No audio/video files found in {INPUT_DIR}")
        print(f"Drop files there and run again.")
        return

    print(f"Found {len(files)} files in {INPUT_DIR}")
    print(f"Loading Whisper model '{MODEL}'...\n")
    model = whisper.load_model(MODEL)

    for i, f in enumerate(files, 1):
        output_path = OUTPUT_DIR / f"{f.stem}_transcript.txt"

        if output_path.exists():
            print(f"[{i}/{len(files)}] {f.name} — already transcribed, skipping")
            continue

        print(f"[{i}/{len(files)}] {f.name} — transcribing...")
        result = model.transcribe(str(f))
        text = result["text"].strip()

        output_path.write_text(text, encoding="utf-8")
        print(f"  -> {output_path.name} ({len(text)} chars)\n")

    print("Done! Transcripts saved to transcripts/")


if __name__ == "__main__":
    main()
