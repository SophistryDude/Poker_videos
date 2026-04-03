"""File watcher — automatically processes new audio files dropped into input_audio/."""

import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from config.settings import INPUT_AUDIO_DIR
from pipeline import run_pipeline

AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm"}


class AudioFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix.lower() in AUDIO_EXTENSIONS:
            # Wait a moment for file to finish writing
            time.sleep(2)
            print(f"\n[Watcher] New audio detected: {path.name}")
            try:
                run_pipeline(path, skip_upload=True)
            except Exception as e:
                print(f"[Watcher] Error processing {path.name}: {e}")


def watch():
    """Watch the input_audio folder for new files and auto-process them."""
    INPUT_AUDIO_DIR.mkdir(exist_ok=True)
    print(f"[Watcher] Watching {INPUT_AUDIO_DIR} for new audio files...")
    print("[Watcher] Drop an audio file in that folder to start processing.")
    print("[Watcher] Press Ctrl+C to stop.\n")

    handler = AudioFileHandler()
    observer = Observer()
    observer.schedule(handler, str(INPUT_AUDIO_DIR), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[Watcher] Stopped.")
    observer.join()


if __name__ == "__main__":
    watch()
