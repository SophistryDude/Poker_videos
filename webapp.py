"""Flask web portal — upload audio from anywhere, track pipeline progress."""

import os
import uuid
import threading
from pathlib import Path
from datetime import datetime

from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename

from config.settings import (
    BASE_DIR, INPUT_AUDIO_DIR, TRANSCRIPTS_DIR,
    CLEANED_SCRIPTS_DIR, VOICE_OUTPUT_DIR, VIDEO_OUTPUT_DIR,
)
from steps.transcribe import transcribe
from steps.cleanup import cleanup_script
from steps.voice_synth import synthesize_voice

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500MB max upload

ALLOWED_EXTENSIONS = {"mp3", "wav", "m4a", "ogg", "flac", "webm", "mp4"}

# In-memory job tracker (swap for Redis/DB in production)
jobs: dict[str, dict] = {}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def run_pipeline_async(job_id: str, audio_path: Path):
    """Run the pipeline in a background thread, updating job status."""
    try:
        jobs[job_id]["status"] = "transcribing"
        transcript_path = transcribe(audio_path)
        jobs[job_id]["transcript"] = str(transcript_path)
        jobs[job_id]["transcript_text"] = transcript_path.read_text(encoding="utf-8")

        jobs[job_id]["status"] = "cleaning"
        script_path = cleanup_script(transcript_path)
        jobs[job_id]["script"] = str(script_path)
        jobs[job_id]["script_text"] = script_path.read_text(encoding="utf-8")

        jobs[job_id]["status"] = "synthesizing"
        try:
            voice_path = synthesize_voice(script_path)
            jobs[job_id]["voice"] = str(voice_path)
            jobs[job_id]["voice_filename"] = voice_path.name
        except Exception as e:
            jobs[job_id]["voice_error"] = str(e)

        jobs[job_id]["status"] = "complete"
        jobs[job_id]["completed_at"] = datetime.now().isoformat()

    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": f"File type not allowed. Use: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

    job_id = str(uuid.uuid4())[:8]
    filename = secure_filename(file.filename)
    save_path = INPUT_AUDIO_DIR / f"{job_id}_{filename}"
    file.save(str(save_path))

    jobs[job_id] = {
        "id": job_id,
        "filename": filename,
        "status": "queued",
        "created_at": datetime.now().isoformat(),
        "audio_path": str(save_path),
    }

    thread = threading.Thread(target=run_pipeline_async, args=(job_id, save_path))
    thread.daemon = True
    thread.start()

    return jsonify({"job_id": job_id, "status": "queued"})


@app.route("/status/<job_id>")
def status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job)


@app.route("/jobs")
def list_jobs():
    return jsonify(list(jobs.values()))


@app.route("/download/<folder>/<filename>")
def download(folder, filename):
    folder_map = {
        "transcripts": TRANSCRIPTS_DIR,
        "scripts": CLEANED_SCRIPTS_DIR,
        "voice": VOICE_OUTPUT_DIR,
        "video": VIDEO_OUTPUT_DIR,
    }
    directory = folder_map.get(folder)
    if not directory:
        return jsonify({"error": "Invalid folder"}), 404
    return send_from_directory(str(directory), filename, as_attachment=True)


if __name__ == "__main__":
    for d in [INPUT_AUDIO_DIR, TRANSCRIPTS_DIR, CLEANED_SCRIPTS_DIR, VOICE_OUTPUT_DIR, VIDEO_OUTPUT_DIR]:
        d.mkdir(exist_ok=True)
    app.run(host="0.0.0.0", port=5000, debug=False)
