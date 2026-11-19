#!/usr/bin/env python3
"""
GHOST VECTOR CTF: recovery terminal (prototype / proof of concept)

Routes
  /                      Phase 1 briefing and ghost telemetry download
  /api/uplink            POST a Phase 1 flag to unlock Phase 2 (when gated)
  /vector                Phase 2 briefing and downloads
  /handshake             HANDSHAKE.SYS final stage
  /api/handshake         POST the four Phase 2 marker codes
  /api/transmit          POST the master coordinate (after judge verification)
  /health                Container health check

Hardening
  - Answers are only ever compared as SHA256 hashes (constant-time).
  - Strict Content-Security-Policy (no inline script), frame and sniff protection.
  - Per-client rate limits on every check endpoint, plus a small fixed delay.
  - JSON-only APIs with a 2 KB body cap and 200-character input cap.
  - Session cookie is HttpOnly and SameSite=Strict (Secure when COOKIE_SECURE=1).
  - Downloads are served from a fixed allow-list, never from user paths.
"""

import hashlib
import hmac
import json
import logging
import os
import secrets
import threading
import time
from collections import defaultdict, deque

from flask import (Flask, abort, jsonify, redirect, render_template,
                   request, send_from_directory, session, url_for)

DATA_DIR = os.environ.get("OUTPUT_DIR", "/app/data")
PHASE2_GATE = os.environ.get("PHASE2_GATE", "open").lower()  # open | gated
PRIZE_KEY_HASH = os.environ.get("PRIZE_KEY_HASH", "").strip().lower()
# Shown only after a correct master coordinate. Players submit it to CTFd.
FLAG_FINAL = os.environ.get("FLAG_FINAL", "").strip()
RATE_LIMIT = int(os.environ.get("RATE_LIMIT", "12"))          # attempts
RATE_WINDOW = int(os.environ.get("RATE_WINDOW", "60"))        # seconds
MAX_INPUT = 200

log = logging.getLogger("ghost-vector")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = Flask(__name__)

_key = os.environ.get("SECRET_KEY", "")
if not _key or _key.startswith("change-me") or len(_key) < 16:
    log.warning("SECRET_KEY is missing or weak. Using a random key for this run. "
                "Set a long random SECRET_KEY in config/flags.env.")
    _key = secrets.token_hex(32)
app.secret_key = _key
app.config.update(
    MAX_CONTENT_LENGTH=2048,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Strict",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1",
    SESSION_COOKIE_NAME="gv_session",
)

if os.environ.get("TRUST_PROXY", "0") == "1":
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

PHASE1_FILES = {"ghost_telemetry.csv"}
PHASE2_FILES = {"vector_telemetry.csv", "starmap.png"}

CSP = ("default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; "
       "connect-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'")


# ------------------------------------------------------------------ helpers

class RateLimiter:
    """Sliding-window limiter per (client, endpoint). Thread safe."""

    def __init__(self):
        self.hits = defaultdict(deque)
        self.lock = threading.Lock()

    def allow(self, key):
        now = time.monotonic()
        with self.lock:
            q = self.hits[key]
            while q and now - q[0] > RATE_WINDOW:
                q.popleft()
            if len(q) >= RATE_LIMIT:
                return False
            q.append(now)
            return True


limiter = RateLimiter()
_hashes = None


def load_hashes():
    global _hashes
    if _hashes is None:
        with open(os.path.join(DATA_DIR, ".hashes.json")) as f:
            _hashes = json.load(f)
    return _hashes


def sha(s):
    return hashlib.sha256(s.strip().upper().encode()).hexdigest()


def strip_wrapper(s):
    s = s.strip()
    if s.lower().startswith("astrosec{") and s.endswith("}"):
        return s[9:-1]
    return s


def phase2_unlocked():
    return PHASE2_GATE == "open" or session.get("phase2")


def slow_down():
    # Small fixed delay on every check to make guessing unattractive.
    time.sleep(0.4)


def json_body():
    if not request.is_json:
        abort(415)
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        abort(400)
    return body


def text_field(body, name):
    v = body.get(name, "")
    if not isinstance(v, str) or len(v) > MAX_INPUT:
        abort(400)
    return v


def check_rate(endpoint):
    if not limiter.allow((request.remote_addr, endpoint)):
        log.warning("rate limit hit: %s on %s", request.remote_addr, endpoint)
        abort(429)


# ------------------------------------------------------------------ security hooks

@app.after_request
def security_headers(resp):
    resp.headers["Content-Security-Policy"] = CSP
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    resp.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    if request.path.startswith("/api/"):
        resp.headers["Cache-Control"] = "no-store"
    return resp


ERRORS = {400: "BAD REQUEST", 403: "ACCESS DENIED", 404: "NOT FOUND",
          405: "METHOD NOT ALLOWED", 413: "REQUEST TOO LARGE",
          415: "JSON REQUIRED", 429: "TOO MANY ATTEMPTS. WAIT A MINUTE.",
          500: "INTERNAL ERROR"}


@app.errorhandler(400)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(405)
@app.errorhandler(413)
@app.errorhandler(415)
@app.errorhandler(429)
@app.errorhandler(500)
def handle_error(e):
    code = getattr(e, "code", 500) or 500
    return jsonify(ok=False, message=ERRORS.get(code, "ERROR")), code


# ------------------------------------------------------------------ pages

@app.route("/")
def index():
    return render_template("index.html", unlocked=phase2_unlocked(), gate=PHASE2_GATE)


@app.route("/download/<name>")
def download(name):
    if name in PHASE1_FILES:
        return send_from_directory(DATA_DIR, name, as_attachment=True)
    if name in PHASE2_FILES:
        if not phase2_unlocked():
            abort(403)
        return send_from_directory(DATA_DIR, name, as_attachment=True)
    abort(404)


@app.route("/vector")
def vector():
    if not phase2_unlocked():
        return redirect(url_for("index"))
    return render_template("vector.html")


@app.route("/handshake")
def handshake():
    if not phase2_unlocked():
        return redirect(url_for("index"))
    return render_template("handshake.html",
                           markers_ok=session.get("markers_ok", False),
                           configured=bool(PRIZE_KEY_HASH))


# ------------------------------------------------------------------ APIs

@app.post("/api/uplink")
def uplink():
    check_rate("uplink")
    flag = text_field(json_body(), "flag")
    slow_down()
    if any(hmac.compare_digest(sha(flag), x) for x in load_hashes()["phase1"]):
        session["phase2"] = True
        return jsonify(ok=True, message="UPLINK ESTABLISHED. Vector channel open.",
                       next=url_for("vector"))
    return jsonify(ok=False, message="CARRIER LOST. Signature not recognized.")


@app.post("/api/handshake")
def api_handshake():
    if not phase2_unlocked():
        abort(403)
    check_rate("handshake")
    codes = json_body().get("codes", [])
    if (not isinstance(codes, list) or len(codes) != 4
            or not all(isinstance(c, str) and len(c) <= MAX_INPUT for c in codes)):
        return jsonify(ok=False, message="FOUR MARKER CODES REQUIRED.")
    slow_down()
    h = load_hashes()["markers"]
    results = [hmac.compare_digest(sha(strip_wrapper(c)), h[i]) for i, c in enumerate(codes)]
    if all(results):
        session["markers_ok"] = True
        log.info("markers locked by %s", request.remote_addr)
        return jsonify(ok=True, results=results, message=(
            "ALL FOUR MARKERS LOCKED. Final alignment requires an ALIGNMENT "
            "SLATE. Report to a judge with your markers and be ready to "
            "explain how you recovered each one."))
    return jsonify(ok=False, results=results,
                   message="ALIGNMENT FAILED. One or more markers rejected.")


@app.post("/api/transmit")
def transmit():
    if not session.get("markers_ok"):
        abort(403)
    check_rate("transmit")
    coord = text_field(json_body(), "coordinate")
    if not PRIZE_KEY_HASH:
        return jsonify(ok=False, message="TRANSMITTER OFFLINE. Staff have not "
                       "configured the master coordinate.")
    slow_down()
    if hmac.compare_digest(sha(coord), PRIZE_KEY_HASH):
        log.info("master coordinate accepted from %s", request.remote_addr)
        msg = "MASTER COORDINATE ACCEPTED. GHOST-01 IS COMING HOME."
        if FLAG_FINAL:
            msg += " Submit this flag to the scoreboard: " + FLAG_FINAL
        else:
            msg += " Show this screen to the judge to complete verification."
        return jsonify(ok=True, message=msg, flag=FLAG_FINAL or None)
    return jsonify(ok=False, message="COORDINATE REJECTED. Check your slate.")


@app.route("/health")
def health():
    return jsonify(status="ok")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "8080")))
