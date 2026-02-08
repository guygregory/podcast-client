"""
MVP Flask Web UI for the Azure Speech Podcast Generation API.

Wraps the existing PodcastClient to provide a browser-based interface
for creating podcasts from local TXT/PDF files.
"""

import os
import sys
import json
import uuid
import base64
import threading
import dataclasses
from pathlib import Path
from datetime import datetime

from flask import Flask, render_template, request, jsonify, send_file
from dotenv import dotenv_values

# ---------------------------------------------------------------------------
# Path setup — allow importing the existing podcast client libraries
# located one level up in the ``python/`` directory.
# ---------------------------------------------------------------------------
PYTHON_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PYTHON_ROOT))

from microsoft_client_podcast.podcast_client import PodcastClient
from microsoft_client_podcast.podcast_const import MAX_PLAIN_TEXT_LENGTH, MAX_BASE64_TEXT_LENGTH
from microsoft_client_podcast.podcast_enum import ContentSourceKind, ContentFileFormatKind, PodcastHostKind, PodcastLengthKind, PodcastStyleKind, PodcastGenderPreferenceKind
from microsoft_client_podcast.podcast_dataclass import (
    PodcastGenerationDefinition,
    PodcastContent,
    PodcastScriptGenerationConfig,
    PodcastTtsConfig,
)
from microsoft_speech_client_common.client_common_enum import OperationStatus

# ---------------------------------------------------------------------------
# App initialisation
# ---------------------------------------------------------------------------
app = Flask(__name__)

INPUT_FILES_DIR = Path(__file__).resolve().parent / "input_files"
LOCALES_CSV = Path(__file__).resolve().parent / "locales.csv"
PODCASTS_DIR = Path(__file__).resolve().parent / "podcasts"
PODCASTS_DIR.mkdir(exist_ok=True)

# In-memory job store  {job_id: {status, error, audio_path, generation, cancel_event, client_info}}
jobs: dict[str, dict] = {}

# ---------------------------------------------------------------------------
# .env loading — look for a .env in the parent ``python/`` directory.
# Each variable is optional; missing values become empty strings.
# ---------------------------------------------------------------------------
_env_path = PYTHON_ROOT / ".env"
_env: dict[str, str] = {}
if _env_path.is_file():
    _env = dotenv_values(_env_path)

ENV_DEFAULTS = {
    "REGION": _env.get("REGION", "") or "eastus",
    "SUB_KEY": _env.get("SUB_KEY", ""),
    "API_VERSION": _env.get("API_VERSION", "") or "2026-01-01-preview",
}


def _load_locales() -> list[str]:
    """Read locale codes from locales.csv (one per line)."""
    locales: list[str] = []
    if LOCALES_CSV.is_file():
        for line in LOCALES_CSV.read_text(encoding="utf-8").splitlines():
            code = line.strip()
            if code:
                locales.append(code)
    return locales


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Serve the single-page UI."""
    locales = _load_locales()
    return render_template("index.html", env=ENV_DEFAULTS, locales=locales)


@app.route("/api/input-files")
def list_input_files():
    """Return PDF/TXT files discovered in the ``input_files/`` folder."""
    files: list[str] = []
    if INPUT_FILES_DIR.is_dir():
        for f in sorted(INPUT_FILES_DIR.iterdir()):
            if f.is_file() and f.suffix.lower() in (".txt", ".pdf"):
                files.append(f.name)
    return jsonify(files=files, preselected="")


@app.route("/api/generate", methods=["POST"])
def generate():
    """
    Accept form data and kick off a podcast generation in a background thread.

    Expected form fields:
        region, sub_key, api_version, target_locale
        file_source  — "upload" | "server"
        server_file  — filename inside input_files/ (when file_source=server)
        file         — uploaded file (when file_source=upload)
    """
    region = request.form.get("region", "").strip()
    sub_key = request.form.get("sub_key", "").strip()
    api_version = request.form.get("api_version", "").strip()
    target_locale = request.form.get("target_locale", "").strip()
    file_source = request.form.get("file_source", "server")

    # Optional podcast options
    voice_name = request.form.get("voice_name", "").strip() or None
    multi_talker = request.form.get("multi_talker_voice_speaker_names", "").strip() or None
    gender_preference = request.form.get("gender_preference", "").strip() or None
    length = request.form.get("length", "").strip() or None
    host = request.form.get("host", "").strip() or None
    style = request.form.get("style", "").strip() or None
    additional_instructions = request.form.get("additional_instructions", "").strip() or None

    # --- Validation ----------------------------------------------------------
    if not region or not sub_key or not api_version or not target_locale:
        return jsonify(error="Region, API Key, API Version and Target Locale are all required."), 400

    # Resolve the file content ------------------------------------------------
    file_path: Path | None = None
    file_ext: str = ""

    if file_source == "upload":
        uploaded = request.files.get("file")
        if not uploaded or uploaded.filename == "":
            return jsonify(error="Please select a file to upload."), 400
        file_ext = os.path.splitext(uploaded.filename)[1].lower()
        if file_ext not in (".txt", ".pdf"):
            return jsonify(error="Only .txt and .pdf files are supported."), 400
        # Save to a temp location inside input_files/
        safe_name = f"upload_{uuid.uuid4().hex[:8]}{file_ext}"
        file_path = INPUT_FILES_DIR / safe_name
        uploaded.save(str(file_path))
    else:
        server_file = request.form.get("server_file", "").strip()
        if not server_file:
            return jsonify(error="Please select a server file."), 400
        file_path = INPUT_FILES_DIR / server_file
        if not file_path.is_file():
            return jsonify(error=f"File not found: {server_file}"), 404
        file_ext = file_path.suffix.lower()

    job_id = f"{datetime.now().strftime('%m%d%Y%H%M%S')}_{target_locale}"
    cancel_event = threading.Event()
    jobs[job_id] = {
        "status": "Starting",
        "error": None,
        "audio_path": None,
        "generation": None,
        "cancel_event": cancel_event,
        "client_info": {"region": region, "sub_key": sub_key, "api_version": api_version},
    }

    # Collect optional podcast options into a dict
    podcast_options = {
        "voice_name": voice_name,
        "multi_talker": multi_talker,
        "gender_preference": gender_preference,
        "length": length,
        "host": host,
        "style": style,
        "additional_instructions": additional_instructions,
    }

    # Fire off background thread ----------------------------------------------
    thread = threading.Thread(
        target=_run_generation,
        args=(job_id, region, sub_key, api_version, target_locale, str(file_path), file_ext, podcast_options),
        daemon=True,
    )
    thread.start()

    return jsonify(job_id=job_id)


@app.route("/api/status/<job_id>")
def job_status(job_id: str):
    """Return the current status of a generation job."""
    job = jobs.get(job_id)
    if job is None:
        return jsonify(error="Job not found"), 404
    return jsonify(
        status=job["status"],
        error=job["error"],
        has_audio=job["audio_path"] is not None,
    )


@app.route("/api/cancel/<job_id>", methods=["POST"])
def cancel_job(job_id: str):
    """Cancel a running generation job."""
    job = jobs.get(job_id)
    if job is None:
        return jsonify(error="Job not found"), 404

    # Signal the background thread to stop
    cancel_event = job.get("cancel_event")
    if cancel_event:
        cancel_event.set()

    # Attempt to delete the generation via the API (best-effort)
    info = job.get("client_info", {})
    if info.get("region") and info.get("sub_key") and info.get("api_version"):
        try:
            client = PodcastClient(
                region=info["region"],
                sub_key=info["sub_key"],
                api_version=info["api_version"],
            )
            client.request_delete_generation(job_id)
        except Exception:
            pass  # best-effort

    job["status"] = "Cancelled"
    return jsonify(status="Cancelled")


@app.route("/api/download/<job_id>")
def download(job_id: str):
    """Serve the completed podcast audio file."""
    job = jobs.get(job_id)
    if job is None or job["audio_path"] is None:
        return jsonify(error="Audio not available"), 404
    return send_file(job["audio_path"], as_attachment=True, download_name=f"{job_id}.mp3")


@app.route("/api/delete-generation/<job_id>", methods=["POST"])
def delete_generation(job_id: str):
    """Delete a podcast generation from the Azure server (best-effort)."""
    job = jobs.get(job_id)
    if job is None:
        return jsonify(error="Job not found"), 404

    info = job.get("client_info", {})
    if not (info.get("region") and info.get("sub_key") and info.get("api_version")):
        return jsonify(error="Missing client credentials for deletion"), 400

    try:
        client = PodcastClient(
            region=info["region"],
            sub_key=info["sub_key"],
            api_version=info["api_version"],
        )
        success, error = client.request_delete_generation(job_id)
        if not success:
            return jsonify(error=f"Delete failed: {error}"), 500
        return jsonify(status="Deleted")
    except Exception as exc:
        return jsonify(error=str(exc)), 500


# ---------------------------------------------------------------------------
# Background generation logic
# ---------------------------------------------------------------------------

def _run_generation(
    job_id: str,
    region: str,
    sub_key: str,
    api_version: str,
    target_locale: str,
    file_path: str,
    file_ext: str,
    podcast_options: dict | None = None,
):
    """Run the full generation lifecycle in a background thread."""
    try:
        jobs[job_id]["status"] = "Creating"

        client = PodcastClient(
            region=region,
            sub_key=sub_key,
            api_version=api_version,
        )

        # Build the request body manually (mirrors PodcastClient logic but
        # we already have the file on disk and need to read it ourselves).
        content = PodcastContent()
        if file_ext == ".txt":
            text = Path(file_path).read_text(encoding="utf-8")
            if len(text) > MAX_PLAIN_TEXT_LENGTH:
                raise ValueError(
                    f"Text file exceeds the {MAX_PLAIN_TEXT_LENGTH // 1024}KB limit. "
                    "Please use a shorter file."
                )
            content.kind = ContentSourceKind.PlainText
            content.fileFormat = ContentFileFormatKind.Txt
            content.text = text
        elif file_ext == ".pdf":
            raw = Path(file_path).read_bytes()
            b64 = base64.b64encode(raw).decode("utf-8")
            if len(b64) > MAX_BASE64_TEXT_LENGTH:
                raise ValueError(
                    f"PDF file exceeds the {MAX_BASE64_TEXT_LENGTH // (1024*1024)}MB base64 limit. "
                    "Please use a smaller file."
                )
            content.kind = ContentSourceKind.FileBase64
            content.fileFormat = ContentFileFormatKind.Pdf
            content.base64Text = b64
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")

        # Build optional config objects from podcast_options
        opts = podcast_options or {}

        script_cfg = PodcastScriptGenerationConfig(
            additionalInstructions=opts.get("additional_instructions"),
            length=PodcastLengthKind(opts["length"]) if opts.get("length") else None,
            style=PodcastStyleKind(opts["style"]) if opts.get("style") else None,
        )

        tts_cfg = PodcastTtsConfig(
            voiceName=opts.get("voice_name"),
            genderPreference=(
                PodcastGenderPreferenceKind(opts["gender_preference"])
                if opts.get("gender_preference") else None
            ),
            multiTalkerVoiceSpeakerNames=opts.get("multi_talker"),
        )

        body = PodcastGenerationDefinition(
            displayName="Web UI Generation",
            description=f"Generated via Web UI at {datetime.now().isoformat()}",
            locale=target_locale,
            host=PodcastHostKind(opts["host"]) if opts.get("host") else None,
            content=content,
            scriptGeneration=script_cfg,
            tts=tts_cfg,
        )

        # PUT — create the generation
        success, error, response_gen, operation_location = client.request_create_generation(
            generation_id=job_id,
            request_body=body,
        )
        if not success:
            jobs[job_id]["status"] = "Failed"
            jobs[job_id]["error"] = error
            return

        # Poll until terminated (check cancellation between polls)
        jobs[job_id]["status"] = "Running"
        cancel_event = jobs[job_id].get("cancel_event")

        # Use a simple polling loop that checks cancellation
        import time
        while True:
            if cancel_event and cancel_event.is_set():
                jobs[job_id]["status"] = "Cancelled"
                return
            try:
                success_poll, error_poll, op = client.request_get_generation(job_id)
                if success_poll and op and op.status in (
                    OperationStatus.Succeeded, OperationStatus.Failed
                ):
                    break
            except Exception:
                pass
            # Wait 5 seconds between polls, but check cancel every second
            for _ in range(5):
                if cancel_event and cancel_event.is_set():
                    jobs[job_id]["status"] = "Cancelled"
                    return
                time.sleep(1)

        # Check cancellation before fetching result
        if cancel_event and cancel_event.is_set():
            jobs[job_id]["status"] = "Cancelled"
            return

        # Fetch the completed generation
        success, error, generation = client.request_get_generation(job_id)
        if not success:
            jobs[job_id]["status"] = "Failed"
            jobs[job_id]["error"] = error
            return

        if generation.status != OperationStatus.Succeeded:
            jobs[job_id]["status"] = "Failed"
            jobs[job_id]["error"] = generation.failureReason or "Generation did not succeed."
            jobs[job_id]["generation"] = _safe_gen_dict(generation)
            return

        # Download the audio file
        audio_url = None
        if generation.output and generation.output.audioFileUrl:
            audio_url = generation.output.audioFileUrl

        if audio_url:
            import urllib3
            http = urllib3.PoolManager()
            resp = http.request("GET", audio_url)
            if resp.status == 200:
                audio_path = PODCASTS_DIR / f"{job_id}.mp3"
                audio_path.write_bytes(resp.data)
                jobs[job_id]["audio_path"] = str(audio_path)

        jobs[job_id]["status"] = "Succeeded"
        jobs[job_id]["generation"] = _safe_gen_dict(generation)

    except Exception as exc:
        jobs[job_id]["status"] = "Failed"
        jobs[job_id]["error"] = str(exc)


def _safe_gen_dict(gen: PodcastGenerationDefinition) -> dict | None:
    """Convert a generation dataclass to a JSON-safe dict, swallowing errors."""
    try:
        return dataclasses.asdict(gen)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Entry-point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(f" * Input files dir : {INPUT_FILES_DIR}")
    print(f" * Podcasts dir    : {PODCASTS_DIR}")
    print(f" * .env loaded     : {_env_path.is_file()}")
    app.run(debug=True, host="127.0.0.1", port=5000)
