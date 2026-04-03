"""Main pipeline orchestrator — chains all steps together."""

import sys
from pathlib import Path

from config.settings import INPUT_AUDIO_DIR
from steps.transcribe import transcribe
from steps.cleanup import cleanup_script
from steps.voice_synth import synthesize_voice
from steps.youtube_upload import upload_to_youtube


def run_pipeline(
    audio_path: str | Path,
    title: str | None = None,
    description: str = "",
    tags: list[str] | None = None,
    skip_voice: bool = False,
    skip_upload: bool = False,
):
    """Run the full content creation pipeline.

    Steps:
      1. Transcribe audio to text (Whisper)
      2. Clean up transcript into a script (Claude)
      3. Synthesize voice from script (ElevenLabs)
      4. Upload to YouTube (optional)
    """
    audio_path = Path(audio_path)
    print(f"\n{'='*60}")
    print(f"  POKER VIDEO PIPELINE — {audio_path.name}")
    print(f"{'='*60}\n")

    # Step 1: Transcribe
    print(">>> STEP 1: Transcribing audio...\n")
    transcript_path = transcribe(audio_path)
    print(f"\n    Raw transcript:\n    {transcript_path}\n")

    # Step 2: Cleanup
    print(">>> STEP 2: Cleaning up script with Claude...\n")
    script_path = cleanup_script(transcript_path)
    print(f"\n    Cleaned script:\n    {script_path}\n")

    # Step 3: Voice synthesis
    if skip_voice:
        print(">>> STEP 3: Skipped (--skip-voice)\n")
        voice_path = None
    else:
        print(">>> STEP 3: Generating AI voice...\n")
        voice_path = synthesize_voice(script_path)
        print(f"\n    Voice audio:\n    {voice_path}\n")

    # Step 4: Upload
    # NOTE: Video creation (Step 5 in the workflow) is manual for now.
    # Use the voice audio + script with a tool like HeyGen, Pictory, or InVideo.
    # Once you have a final video file, the upload step handles the rest.
    if skip_upload:
        print(">>> STEP 4: Skipped (--skip-upload)\n")
    else:
        video_files = list(Path("video_output").glob("*.mp4"))
        if not video_files:
            print(">>> STEP 4: No video file found in video_output/")
            print("    Create your video using HeyGen/Pictory/InVideo,")
            print("    save it to video_output/, then run:")
            print("    python -m steps.youtube_upload <video_file> <title>\n")
        else:
            video_path = video_files[-1]  # most recent
            video_title = title or audio_path.stem.replace("_", " ").title()
            print(f">>> STEP 4: Uploading {video_path.name} to YouTube...\n")
            video_id = upload_to_youtube(
                video_path, video_title, description, tags
            )
            print(f"\n    YouTube URL: https://youtube.com/watch?v={video_id}\n")

    print(f"{'='*60}")
    print("  PIPELINE COMPLETE")
    print(f"{'='*60}")
    print("\nOutputs:")
    print(f"  Transcript:    {transcript_path}")
    print(f"  Script:        {script_path}")
    if voice_path:
        print(f"  Voice audio:   {voice_path}")
    print()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Poker Video Content Pipeline")
    parser.add_argument("audio", help="Path to input audio file")
    parser.add_argument("--title", help="Video title (defaults to filename)")
    parser.add_argument("--description", default="", help="Video description")
    parser.add_argument("--tags", nargs="+", default=["poker"], help="Video tags")
    parser.add_argument("--skip-voice", action="store_true", help="Skip voice synthesis")
    parser.add_argument("--skip-upload", action="store_true", help="Skip YouTube upload")

    args = parser.parse_args()

    run_pipeline(
        audio_path=args.audio,
        title=args.title,
        description=args.description,
        tags=args.tags,
        skip_voice=args.skip_voice,
        skip_upload=args.skip_upload,
    )


if __name__ == "__main__":
    main()
