#!/usr/bin/env python3
"""
GHOST VECTOR CTF: recovery terminal (prototype / proof of concept)

Routes
  /                      Phase 1 briefing and ghost telemetry download
  /api/uplink            POST a Phase 1 flag to unlock Phase 2
  /vector                Phase 2 briefing and downloads
  /handshake             HANDSHAKE.SYS final stage
  /api/handshake         POST the four Phase 2 marker codes
  /api/transmit          POST the master coordinate (after judge verification)
  /health                Container health check
"""

import hashlib
import hmac
import json
import os
import secrets
import time

from flask import (Flask, abort, jsonify, redirect, render_template,
                   request, send_from_directory, session, url_for)

DATA_DIR = os.environ.get("OUTPUT_DIR", "/app/data")
PHASE2_GATE = os.environ.get("PHASE2_GATE", "gated").lower()  # gated | open
PRIZE_KEY_HASH = os.environ.get("PRIZE_KEY_HASH", "").strip().lower()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

PHASE1_FILES = {"ghost_telemetry.csv"}
PHASE2_FILES = {"vector_telemetry.csv", "starmap.png"}


def load_hashes():
    with open(os.path.join(DATA_DIR, ".hashes.json")) as f:
        return json.load(f)


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
    # Small fixed delay to make brute forcing the API unattractive.
    time.sleep(0.4)


@app.route("/")
def index():
    return render_template("index.html", unlocked=phase2_unlocked(),
                           gate=PHASE2_GATE)


@app.route("/download/<name>")
def download(name):
    if name in PHASE1_FILES:
        return send_from_directory(DATA_DIR, name, as_attachment=True)
    if name in PHASE2_FILES:
        if not phase2_unlocked():
            abort(403)
        return send_from_directory(DATA_DIR, name, as_attachment=True)
    abort(404)


@app.post("/api/uplink")
def uplink():
    slow_down()
    flag = (request.get_json(silent=True) or {}).get("flag", "")
    h = load_hashes()
    if any(hmac.compare_digest(sha(flag), x) for x in h["phase1"]):
        session["phase2"] = True
        return jsonify(ok=True, message="UPLINK ESTABLISHED. Vector channel open.",
                       next=url_for("vector"))
    return jsonify(ok=False, message="CARRIER LOST. Signature not recognized.")


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


@app.post("/api/handshake")
def api_handshake():
    if not phase2_unlocked():
        abort(403)
    slow_down()
    codes = (request.get_json(silent=True) or {}).get("codes", [])
    if not isinstance(codes, list) or len(codes) != 4:
        return jsonify(ok=False, message="FOUR MARKER CODES REQUIRED.")
    h = load_hashes()["markers"]
    results = [hmac.compare_digest(sha(strip_wrapper(str(c))), h[i])
               for i, c in enumerate(codes)]
    if all(results):
        session["markers_ok"] = True
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
    slow_down()
    if not PRIZE_KEY_HASH:
        return jsonify(ok=False, message="TRANSMITTER OFFLINE. Staff have not "
                       "configured the master coordinate.")
    coord = (request.get_json(silent=True) or {}).get("coordinate", "")
    if hmac.compare_digest(sha(coord), PRIZE_KEY_HASH):
        return jsonify(ok=True, message=(
            "MASTER COORDINATE ACCEPTED. GHOST-01 IS COMING HOME. "
            "Show this screen to the judge to complete verification."))
    return jsonify(ok=False, message="COORDINATE REJECTED. Check your slate.")


@app.route("/health")
def health():
    return jsonify(status="ok")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
