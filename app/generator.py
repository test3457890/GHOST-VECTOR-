#!/usr/bin/env python3
"""
GHOST VECTOR CTF: challenge data generator (prototype / proof of concept)

Merges two AstroSec challenges into one storyline:

  PHASE 1, GHOST SIGNAL (formerly "Ghost Satellite")
    File: ghost_telemetry.csv (5,000 rows, nominal 5 second cadence)
    G1  Rows where Battery_pct is exactly 0 carry one flag character each.
        Signal_Strength_dBm on those rows is the ASCII code.
    G2  The nominal gap between samples is 5 seconds. Anomalous gaps,
        in order, equal the ASCII codes of the flag characters.
    G3  Transceiver_Temp_C is written to 3 decimals (millidegrees). The
        least significant bit of each millidegree value, starting at the
        first row, carries the flag bits (8 bits per char, MSB first).

  PHASE 2, SILENT VECTOR (formerly "Project Silent Vector")
    Files: vector_telemetry.csv, starmap.png
    V1  Rows where Frequency_MHz is exactly 1420.400 are markers. The
        Pulse_Duration of the first markers, in order, is ASCII.
    V2  Time gaps between consecutive markers are Morse code:
        2 s dot, 5 s dash, 1 s between symbols, 3 s between characters.
    V3  starmap.png hides text drawn in #010101 on a #000000 sky.
    V4  Among NON-marker rows, take rows whose Pulse_Duration is prime.
        The first N prime values mod 127 are ASCII codes of the flag.

  FINAL STAGE, HANDSHAKE.SYS
    The four Phase 2 marker codes are checked against SHA256 hashes only.
    The master coordinate is built by hand from a physical slate card the
    judge holds. Only a SHA256 hash of the master coordinate is configured.

All flags come from environment variables (see config/flags.example.env),
so no real flag is ever committed to the repository.
"""

import csv
import hashlib
import json
import math
import os
import random
from datetime import datetime, timedelta

from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "/app/data")
SEED = int(os.environ.get("SEED", "1420"))

G1 = os.environ.get("FLAG_G1", "AstroSec{CHANGE_ME_G1}")
G2 = os.environ.get("FLAG_G2", "AstroSec{CHANGE_ME_G2}")
G3 = os.environ.get("FLAG_G3", "AstroSec{CHANGE_ME_G3}")
V1 = os.environ.get("CODE_V1", "NAV_CHANGEME_SYNC_1")
V2 = os.environ.get("CODE_V2", "NAV_CHANGEME_VECTOR_2")
V3 = os.environ.get("CODE_V3", "NAV_CHANGEME_COORD_3")
V4 = os.environ.get("CODE_V4", "NAV_CHANGEME_PRIME_4")

MORSE = {
    "A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.",
    "G": "--.", "H": "....", "I": "..", "J": ".---", "K": "-.-", "L": ".-..",
    "M": "--", "N": "-.", "O": "---", "P": ".--.", "Q": "--.-", "R": ".-.",
    "S": "...", "T": "-", "U": "..-", "V": "...-", "W": ".--", "X": "-..-",
    "Y": "-.--", "Z": "--..", "0": "-----", "1": ".----", "2": "..---",
    "3": "...--", "4": "....-", "5": ".....", "6": "-....", "7": "--...",
    "8": "---..", "9": "----.", "_": "..--.-",
}

MARKER_FREQ = 1420.400


def is_prime(n):
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def sha(s):
    return hashlib.sha256(s.strip().upper().encode()).hexdigest()


# ---------------------------------------------------------------- PHASE 1

def generate_ghost(rng):
    rows = 5000
    start = datetime(2026, 3, 14, 4, 0, 0)

    # G1: choose rows for Battery == 0
    g1_rows = sorted(rng.sample(range(200, rows - 200), len(G1)))
    # G2: choose rows whose gap BEFORE them is anomalous (not on G1 rows)
    pool = [r for r in range(300, rows - 100) if r not in set(g1_rows)]
    g2_rows = sorted(rng.sample(pool, len(G2)))
    g2_map = {r: ord(c) for r, c in zip(g2_rows, G2)}
    g1_map = {r: ord(c) for r, c in zip(g1_rows, G1)}

    # G3: bit stream for first rows
    bits = []
    for c in G3:
        bits.extend(int(b) for b in format(ord(c), "08b"))

    path = os.path.join(OUTPUT_DIR, "ghost_telemetry.csv")
    t = start
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Timestamp", "Altitude_km", "Battery_pct",
                    "Transceiver_Temp_C", "Signal_Strength_dBm"])
        for i in range(rows):
            if i > 0:
                t += timedelta(seconds=g2_map.get(i, 5))
            phase = 2 * math.pi * i / 1100.0
            alt = 545.0 + 12.0 * math.sin(phase) + rng.uniform(-0.4, 0.4)
            batt = 62 + 25 * math.sin(phase + 1.3) + rng.uniform(-3, 3)
            batt = max(4.0, min(99.0, batt))
            temp_m = int(round((18.0 + 9.0 * math.sin(phase + 0.6)
                                + rng.uniform(-0.6, 0.6)) * 1000))
            if i < len(bits):
                temp_m = (temp_m & ~1) | bits[i]
            sig = -78 + 9 * math.sin(phase * 3) + rng.uniform(-4, 4)
            if i in g1_map:
                batt = 0.0
                sig = g1_map[i]
            w.writerow([t.strftime("%Y-%m-%dT%H:%M:%SZ"), f"{alt:.3f}",
                        f"{batt:.1f}", f"{temp_m / 1000:.3f}",
                        f"{sig:.1f}" if i not in g1_map else f"{sig}"])
    return path


# ---------------------------------------------------------------- PHASE 2

def morse_intervals(text):
    out = []
    for i, ch in enumerate(text.upper()):
        seq = MORSE[ch]
        for j, s in enumerate(seq):
            out.append(2 if s == "." else 5)
            if j < len(seq) - 1:
                out.append(1)
        if i < len(text) - 1:
            out.append(3)
    return out


def prime_with_residue(rng, residue, used):
    while True:
        k = rng.randint(3, 60)
        p = residue + 127 * k
        if is_prime(p) and p not in used:
            used.add(p)
            return p


def nonprime(rng, lo=200, hi=4000):
    while True:
        n = rng.randint(lo, hi)
        if not is_prime(n):
            return n


def random_freq(rng):
    while True:
        f = round(rng.uniform(1418.0, 1423.0), 3)
        if abs(f - MARKER_FREQ) > 0.0005:
            return f


def generate_vector(rng):
    gaps = morse_intervals(V2)
    n_markers = len(gaps) + 1
    v1_ascii = [ord(c) for c in V1]
    v4_primes_needed = [ord(c) for c in V4]
    used = set()
    start = datetime(2026, 3, 15, 22, 0, 0)
    fillers_between = 3

    rows = []
    t = 0.0  # seconds since start, ms precision
    prime_slots = list(v4_primes_needed)
    for m in range(n_markers):
        # marker row
        pd = v1_ascii[m] if m < len(v1_ascii) else nonprime(rng, 20, 126)
        rows.append((t, MARKER_FREQ, pd, True))
        if m < len(gaps):
            gap = gaps[m]
            for k in range(1, fillers_between + 1):
                ft = t + gap * k / (fillers_between + 1) + rng.uniform(-0.05, 0.05)
                if prime_slots and rng.random() < 0.5:
                    fpd = prime_with_residue(rng, prime_slots.pop(0), used)
                else:
                    fpd = nonprime(rng)
                rows.append((ft, random_freq(rng), fpd, False))
            t += gap
    # trailing filler: leftover primes then 300 decoy rows (more primes)
    for res in prime_slots:
        t += 0.8
        rows.append((t, random_freq(rng), prime_with_residue(rng, res, used), False))
    for _ in range(300):
        t += rng.uniform(0.4, 1.6)
        if rng.random() < 0.3:
            fpd = prime_with_residue(rng, rng.randint(1, 126), used)
        else:
            fpd = nonprime(rng)
        rows.append((t, random_freq(rng), fpd, False))

    path = os.path.join(OUTPUT_DIR, "vector_telemetry.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Timestamp", "Frequency_MHz", "Pulse_Duration",
                    "Gain_dB", "Doppler_Hz"])
        for (ts, fr, pd, _m) in rows:
            stamp = (start + timedelta(seconds=round(ts, 3)))
            w.writerow([stamp.strftime("%Y-%m-%dT%H:%M:%S.") +
                        f"{stamp.microsecond // 1000:03d}Z",
                        f"{fr:.3f}", pd,
                        f"{rng.uniform(28, 41):.2f}",
                        f"{rng.uniform(-4200, 4200):.1f}"])
    return path


def generate_starmap(rng):
    W, H = 1600, 900
    img = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default(size=56)
    except TypeError:
        font = ImageFont.load_default()
    for _ in range(1400):
        x, y = rng.randint(0, W - 1), rng.randint(0, H - 1)
        b = rng.randint(90, 255)
        r = rng.choice([0, 0, 0, 1])
        d.ellipse((x - r, y - r, x + r, y + r), fill=(b, b, min(255, b + 20)))
    # Text is drawn on top of the stars so no star-free gap gives it away.
    tx, ty = rng.randint(80, 600), rng.randint(120, 720)
    d.text((tx, ty), V3, fill=(1, 1, 1), font=font)
    path = os.path.join(OUTPUT_DIR, "starmap.png")
    img.save(path)
    return path


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    rng = random.Random(SEED)
    generate_ghost(rng)
    generate_vector(rng)
    generate_starmap(rng)
    # Hash store used by the web app. Never served to players.
    hashes = {
        "phase1": [sha(G1), sha(G2), sha(G3)],
        "markers": [sha(V1), sha(V2), sha(V3), sha(V4)],
    }
    with open(os.path.join(OUTPUT_DIR, ".hashes.json"), "w") as f:
        json.dump(hashes, f)
    print(f"[generator] challenge data written to {OUTPUT_DIR} (seed {SEED})")


if __name__ == "__main__":
    main()
