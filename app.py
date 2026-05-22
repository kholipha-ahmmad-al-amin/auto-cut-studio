from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

from smartcut import MODES, ROOT, process_video


UPLOAD_DIR = ROOT / "uploads"
OUTPUT_DIR = ROOT / "outputs"
ALLOWED_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v", ".wav", ".mp3", ".flac"}

app = Flask(__name__)
jobs: dict[str, dict] = {}
jobs_lock = threading.Lock()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def allowed_file(path: Path) -> bool:
    return path.suffix.lower() in ALLOWED_EXTENSIONS


def append_log(job_id: str, message: str) -> None:
    with jobs_lock:
        job = jobs.get(job_id)
        if job is not None:
            job["logs"].append(message)


def update_job(job_id: str, **values) -> None:
    with jobs_lock:
        job = jobs.get(job_id)
        if job is not None:
            job.update(values)


def run_job(job_id: str, files: list[Path], mode_key: str) -> None:
    results = []
    update_job(job_id, status="running", started_at=utc_now())

    try:
        for index, input_path in enumerate(files, start=1):
            update_job(job_id, current=index, total=len(files))
            append_log(job_id, f"Processing {input_path.name}")
            output_path = process_video(input_path, mode_key, OUTPUT_DIR, lambda msg: append_log(job_id, msg))
            results.append(
                {
                    "name": output_path.name,
                    "download_url": f"/download/{output_path.name}",
                    "size": output_path.stat().st_size,
                }
            )

        update_job(job_id, status="finished", finished_at=utc_now(), results=results)
    except Exception as exc:
        append_log(job_id, str(exc))
        update_job(job_id, status="failed", finished_at=utc_now(), results=results)


@app.get("/")
def index():
    mode_list = [mode for mode in MODES.values()]
    return render_template("index.html", modes=mode_list)


@app.get("/api/modes")
def modes():
    return jsonify(
        [
            {
                "key": mode.key,
                "label": mode.label,
                "description": mode.description,
                "suffix": mode.suffix,
            }
            for mode in MODES.values()
        ]
    )


@app.post("/api/jobs")
def create_job():
    mode_key = request.form.get("mode", "normal")
    uploaded_files = request.files.getlist("files")

    if not uploaded_files:
        return jsonify({"error": "No files were uploaded."}), 400

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    saved_files = []

    for uploaded in uploaded_files:
        original_name = uploaded.filename or "video"
        safe_name = secure_filename(original_name)
        file_path = Path(safe_name)

        if not safe_name or not allowed_file(file_path):
            return jsonify({"error": f"Unsupported file type: {original_name}"}), 400

        unique_name = f"{uuid.uuid4().hex[:8]}-{safe_name}"
        destination = UPLOAD_DIR / unique_name
        uploaded.save(destination)
        saved_files.append(destination)

    job_id = uuid.uuid4().hex
    with jobs_lock:
        jobs[job_id] = {
            "id": job_id,
            "mode": mode_key,
            "status": "queued",
            "current": 0,
            "total": len(saved_files),
            "logs": ["Job queued"],
            "results": [],
            "created_at": utc_now(),
        }

    thread = threading.Thread(target=run_job, args=(job_id, saved_files, mode_key), daemon=True)
    thread.start()

    return jsonify({"job_id": job_id})


@app.get("/api/jobs/<job_id>")
def get_job(job_id: str):
    with jobs_lock:
        job = jobs.get(job_id)
        if job is None:
            return jsonify({"error": "Job was not found."}), 404
        return jsonify(job)


@app.get("/download/<path:filename>")
def download(filename: str):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=7860, debug=False)
