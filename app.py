import os
import re
import shutil
import tempfile
import threading
import time
import uuid
from urllib.parse import urlparse

from flask import Flask, abort, jsonify, render_template, request, send_file
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_ROOT = os.path.join(tempfile.gettempdir(), "yt-downloads")
COOKIES_FILE = os.environ.get("COOKIES_FILE", os.path.join(BASE_DIR, "cookies.txt"))
FILE_TTL_SECONDS = 15 * 60

ALLOWED_HOSTS = {
    "youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be",
}
JOB_ID_RE = re.compile(r"^[0-9a-f]{32}$")

os.makedirs(DOWNLOAD_ROOT, exist_ok=True)


def is_youtube_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    return parsed.scheme in ("http", "https") and (parsed.hostname or "").lower() in ALLOWED_HOSTS


def build_options(job_dir: str, fmt: str) -> dict:
    opts = {
        "outtmpl": os.path.join(job_dir, "%(title).150B.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "restrictfilenames": False,
        "socket_timeout": 60,
        "format": "bestaudio/best" if fmt == "audio" else "best[ext=mp4]/best",
    }
    if os.path.isfile(COOKIES_FILE):
        opts["cookiefile"] = COOKIES_FILE
    return opts


def cleanup_loop():
    """מוחק תיקיות הורדה ישנות כדי שהדיסק לא יתמלא."""
    while True:
        time.sleep(60)
        cutoff = time.time() - FILE_TTL_SECONDS
        for name in os.listdir(DOWNLOAD_ROOT):
            path = os.path.join(DOWNLOAD_ROOT, name)
            try:
                if os.path.getmtime(path) < cutoff:
                    shutil.rmtree(path, ignore_errors=True)
            except OSError:
                pass


threading.Thread(target=cleanup_loop, daemon=True).start()


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/healthz")
def healthz():
    return "ok"


@app.post("/api/download")
def api_download():
    data = request.get_json(silent=True) or request.form
    url = (data.get("url") or "").strip()
    fmt = data.get("format", "video")

    if fmt not in ("video", "audio"):
        return jsonify(error="פורמט לא נתמך"), 400
    if not is_youtube_url(url):
        return jsonify(error="יש להזין קישור תקין של יוטיוב"), 400

    job_id = uuid.uuid4().hex
    job_dir = os.path.join(DOWNLOAD_ROOT, job_id)
    os.makedirs(job_dir)

    try:
        with YoutubeDL(build_options(job_dir, fmt)) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
    except DownloadError as e:
        shutil.rmtree(job_dir, ignore_errors=True)
        msg = re.sub(r"\x1b\[[0-9;]*m", "", str(e)).replace("ERROR: ", "")
        return jsonify(error=f"ההורדה נכשלה: {msg}"), 422
    except Exception:
        shutil.rmtree(job_dir, ignore_errors=True)
        app.logger.exception("unexpected download failure")
        return jsonify(error="אירעה שגיאה בלתי צפויה"), 500

    return jsonify(
        title=info.get("title", ""),
        filename=os.path.basename(path),
        url=f"/files/{job_id}",
    )


@app.get("/files/<job_id>")
def get_file(job_id):
    if not JOB_ID_RE.match(job_id):
        abort(404)
    job_dir = os.path.join(DOWNLOAD_ROOT, job_id)
    if not os.path.isdir(job_dir):
        abort(404)
    files = os.listdir(job_dir)
    if not files:
        abort(404)
    return send_file(os.path.join(job_dir, files[0]), as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
