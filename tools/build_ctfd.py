#!/usr/bin/env python3
"""Build a CTFd challenge pack for GHOST VECTOR (prototype / proof of concept).

Reads your flags from config/flags.env, generates the exact same challenge
files the terminal serves (same flags + same SEED = same files), and writes
one ctfcli-ready folder per challenge:

    ctfd/build/
      01-g1-power-loss/challenge.yml
      01-g1-power-loss/files/ghost_telemetry.csv
      ...
      08-final-bring-it-home/challenge.yml
      MANUAL_ENTRY.md        (same data, for clicking it into CTFd by hand)

ctfd/build/ contains real flags. It is git ignored. Never commit it.

Usage:
    python3 tools/build_ctfd.py                       # uses config/flags.env
    python3 tools/build_ctfd.py --env other.env --out /tmp/pack
    python3 tools/build_ctfd.py --dynamic             # CTFd dynamic scoring
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GENERATOR = ROOT / "app" / "generator.py"
AUTHOR = "Stuff Studios"

GHOST = "files/ghost_telemetry.csv"
VECTOR = "files/vector_telemetry.csv"
STARMAP = "files/starmap.png"

STORY_P1 = (
    "Experimental relay satellite **GHOST-01** was declared lost eleven years "
    "ago. It just woke up and is broadcasting a corrupted housekeeping stream "
    "on a dead downlink. Download `ghost_telemetry.csv` and find what is "
    "hiding inside it."
)
STORY_P2 = (
    "The ghost signal was a handshake. GHOST-01 has opened a second channel on "
    "the hydrogen line and is sending fragments of its navigation solution. "
    "Recover the marker code. Codes look like `NAV_WORD_WORD_N`. Submit it "
    "as-is or wrapped as `AstroSec{NAV_...}`."
)


def challenges(env):
    """Every challenge, in board order. Hints match docs/HINTS.md."""
    g1, g2, g3 = env["FLAG_G1"], env["FLAG_G2"], env["FLAG_G3"]
    v = [env["CODE_V1"], env["CODE_V2"], env["CODE_V3"], env["CODE_V4"]]
    final = env.get("FLAG_FINAL", "")
    url = env.get("TERMINAL_URL", "http://localhost:8080")
    p1 = "Phase 1: Ghost Signal"
    p2 = "Phase 2: Silent Vector"
    p3 = "Final: Handshake"
    first = "G1 Power Loss"

    def marker(code):
        return [code, "AstroSec{" + code + "}"]

    return [
        dict(slug="01-g1-power-loss", name=first, category=p1, value=100,
             tags=["forensics", "csv", "ascii", "easy"], files=[GHOST],
             flags=[g1],
             text=STORY_P1 + "\n\n**[G1]** Something is wrong with the power readings.",
             hints=["A satellite with a working downlink should never report a completely empty battery.",
                    "Filter for rows where `Battery_pct` is exactly 0. Look at the other values on those rows.",
                    "On those rows `Signal_Strength_dBm` is a positive whole number. Look it up in an ASCII table."]),
        dict(slug="02-g2-clock-drift", name="G2 Clock Drift", category=p1, value=200,
             tags=["forensics", "time-series", "medium"], files=[GHOST],
             flags=[g2],
             text=STORY_P1 + "\n\n**[G2]** The clock is not keeping time.",
             hints=["The satellite samples on a regular schedule. Work out what that schedule is.",
                    "Calculate the time between each row and the next. Most gaps are identical.",
                    "Each unusual gap, measured in seconds, is a character code."]),
        dict(slug="03-g3-thermal-whisper", name="G3 Thermal Whisper", category=p1, value=300,
             tags=["forensics", "steganography", "lsb", "hard"], files=[GHOST],
             flags=[g3],
             text=STORY_P1 + "\n\n**[G3]** The thermal sensor is whispering, one bit at a time.",
             hints=["The temperature is recorded with more precision than any real sensor needs.",
                    "Multiply by 1000 to get whole millidegrees. Is each value odd or even?",
                    "Start at the first row. Take the lowest bit of each value, group into 8 bits, decode as ASCII."]),
        dict(slug="04-v1-sync", name="V1 SYNC", category=p2, value=150,
             tags=["signals", "pattern-recognition", "easy"], files=[VECTOR],
             flags=marker(v[0]), requires=[first],
             text=STORY_P2 + "\n\n**[V1 SYNC]** The satellite keeps returning to one exact frequency.",
             hints=["One frequency appears far more often than chance allows. Radio astronomers know it well.",
                    "Filter for `Frequency_MHz == 1420.400`.",
                    "Read `Pulse_Duration` on those rows, in order, as ASCII."]),
        dict(slug="05-v2-vector", name="V2 VECTOR", category=p2, value=250,
             tags=["signals", "timing", "morse", "medium"], files=[VECTOR],
             flags=marker(v[1]), requires=[first],
             text=STORY_P2 + "\n\n**[V2 VECTOR]** Listen to the rhythm between those returns.",
             hints=["Ignore what the marker rows say. Look at when they happen.",
                    "Calculate the gaps between consecutive 1420.400 rows. Only a few distinct values appear.",
                    "Two values are short and long signals. The others are pauses. Think telegraph."]),
        dict(slug="06-v3-coord", name="V3 COORD", category=p2, value=200,
             tags=["steganography", "image", "medium"], files=[STARMAP],
             flags=marker(v[2]), requires=[first],
             text=STORY_P2 + "\n\n**[V3 COORD]** The star map is darker than it looks.",
             hints=["The sky in the star map is not all the same black.",
                    "Inspect exact pixel values, or push brightness and levels to the maximum.",
                    "Pixels that are exactly (1,1,1) form text."]),
        dict(slug="07-v4-prime", name="V4 PRIME", category=p2, value=350,
             tags=["math", "primes", "modular-arithmetic", "hard"], files=[VECTOR],
             flags=marker(v[3]), requires=[first],
             text=STORY_P2 + "\n\n**[V4 PRIME]** Only the indivisible pulses matter. Count them modulo 127.",
             hints=["Exclude the marker rows. Some of the remaining pulse durations can only be divided by 1 and themselves.",
                    "Keep only the prime `Pulse_Duration` values, in file order.",
                    "Take each prime mod 127 and read the result as ASCII."]),
        dict(slug="08-final-bring-it-home", name="FINAL Bring It Home", category=p3, value=500,
             tags=["final", "judge-verified"], files=[],
             flags=[final] if final else [],
             requires=["V1 SYNC", "V2 VECTOR", "V3 COORD", "V4 PRIME"],
             connection_info=url + "/handshake",
             text=("All four navigation markers are recovered. Now bring GHOST-01 home.\n\n"
                   "1. Open **HANDSHAKE.SYS** on the recovery terminal and lock in all four markers.\n"
                   "2. Find a judge. Be ready to explain how you recovered **each** marker.\n"
                   "3. If you pass, the judge gives you an **alignment slate**.\n"
                   "4. Use the slate to build the master coordinate and transmit it.\n"
                   "5. The terminal reveals the final flag. Submit it here.\n\n"
                   "There are no hints for this stage. The rule only exists on paper."),
             hints=[]),
    ]


def hint_costs(value):
    """First hint free, then 10 percent, then 25 percent of the points."""
    return [0, round(value * 0.10), round(value * 0.25)]


def yaml_str(s):
    """Double-quoted YAML scalar."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def yaml_block(s, indent="  "):
    return "|-\n" + "\n".join(indent + line if line else "" for line in s.split("\n"))


def render_yaml(c, dynamic):
    out = [
        f"name: {yaml_str(c['name'])}",
        f"author: {yaml_str(AUTHOR)}",
        f"attribution: {yaml_str('Written by ' + AUTHOR + ' for the GHOST VECTOR CTF prototype')}",
        f"category: {yaml_str(c['category'])}",
        "description: " + yaml_block(c["text"]),
    ]
    if dynamic:
        out += ["type: dynamic", "extra:",
                f"  initial: {c['value']}",
                "  decay: 10",
                f"  minimum: {max(50, c['value'] // 4)}"]
    else:
        out += ["type: standard", f"value: {c['value']}"]
    if c.get("connection_info"):
        out.append(f"connection_info: {yaml_str(c['connection_info'])}")
    if c["flags"]:
        out.append("flags:")
        for f in c["flags"]:
            out += ["  - type: static", f"    content: {yaml_str(f)}",
                    "    data: case_insensitive"]
    out.append("tags:")
    out += [f"  - {yaml_str(t)}" for t in c["tags"]]
    if c["files"]:
        out.append("files:")
        out += [f"  - {f}" for f in c["files"]]
    if c["hints"]:
        out.append("hints:")
        for h, cost in zip(c["hints"], hint_costs(c["value"])):
            out += [f"  - content: {yaml_str(h)}", f"    cost: {cost}"]
    if c.get("requires"):
        out.append("requirements:")
        out += [f"  - {yaml_str(r)}" for r in c["requires"]]
    out += ["state: visible", 'version: "0.1"', ""]
    return "\n".join(out)


def load_env(path):
    env = {}
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env


def validate(env):
    problems = []
    for k in ["FLAG_G1", "FLAG_G2", "FLAG_G3", "CODE_V1", "CODE_V2", "CODE_V3", "CODE_V4"]:
        if not env.get(k):
            problems.append(f"{k} is missing")
    if env.get("CODE_V2") and not all(ch.isalnum() or ch == "_" for ch in env["CODE_V2"]):
        problems.append("CODE_V2 may only use A-Z, 0-9 and _ (it is sent as Morse)")
    for k in ["FLAG_G1", "FLAG_G2", "FLAG_G3", "FLAG_FINAL"]:
        if env.get(k) and not all(32 < ord(ch) < 127 for ch in env[k]):
            problems.append(f"{k} must be printable ASCII without spaces")
    return problems


def manual_entry(chals, dynamic):
    lines = ["# CTFd Manual Entry Sheet", "",
             "**CONFIDENTIAL: contains flags.** Generated by tools/build_ctfd.py.", "",
             "Use this if you are adding challenges by hand in CTFd Admin > Challenges > +.",
             "Flags are static and case insensitive. Upload the files listed from this folder.", ""]
    for c in chals:
        lines += [f"## {c['name']}", "",
                  f"- **Category:** {c['category']}",
                  f"- **Points:** {c['value']}" + (" (dynamic, decay 10)" if dynamic else ""),
                  f"- **Flags:** " + (", ".join(f"`{f}`" for f in c['flags']) or "none (judge awarded)"),
                  f"- **Files:** " + (", ".join(c['files']) or "none"),
                  f"- **Prerequisites:** " + (", ".join(c.get('requires', [])) or "none")]
        if c.get("connection_info"):
            lines.append(f"- **Connection info:** {c['connection_info']}")
        lines += ["", "**Description:**", "", c["text"], ""]
        if c["hints"]:
            lines.append("**Hints:**")
            lines.append("")
            for i, (h, cost) in enumerate(zip(c["hints"], hint_costs(c["value"])), 1):
                lines.append(f"{i}. ({cost} pts) {h}")
            lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--env", default=str(ROOT / "config" / "flags.env"))
    ap.add_argument("--out", default=str(ROOT / "ctfd" / "build"))
    ap.add_argument("--dynamic", action="store_true", help="use CTFd dynamic scoring")
    args = ap.parse_args()

    if not Path(args.env).exists():
        sys.exit(f"{args.env} not found. Copy config/flags.example.env to config/flags.env first.")
    env = load_env(args.env)
    problems = validate(env)
    if problems:
        sys.exit("Fix config first:\n  " + "\n  ".join(problems))
    if any("CHANGE_ME" in env.get(k, "") for k in env):
        print("WARNING: some flags still contain CHANGE_ME. Fine for testing, not for an event.")

    out = Path(args.out)
    if out.exists():
        shutil.rmtree(out)
    data = out / "_data"
    data.mkdir(parents=True)
    run_env = dict(os.environ, **env, OUTPUT_DIR=str(data))
    subprocess.run([sys.executable, str(GENERATOR)], env=run_env, check=True)

    chals = challenges(env)
    for c in chals:
        d = out / c["slug"]
        (d / "files").mkdir(parents=True)
        for f in c["files"]:
            shutil.copy(data / Path(f).name, d / f)
        (d / "challenge.yml").write_text(render_yaml(c, args.dynamic))
    (out / "MANUAL_ENTRY.md").write_text(manual_entry(chals, args.dynamic))
    shutil.rmtree(data)

    if not env.get("FLAG_FINAL"):
        print("NOTE: FLAG_FINAL is blank, so FINAL has no flag. Award it by hand in CTFd.")
    if not env.get("PRIZE_KEY_HASH"):
        print("NOTE: PRIZE_KEY_HASH is blank. Run tools/set_prize_key.py before the event.")
    print(f"Built {len(chals)} CTFd challenges in {out}")
    print("Next: see docs/CTFD_SETUP.md (ctf challenge install, or MANUAL_ENTRY.md by hand).")


if __name__ == "__main__":
    main()
