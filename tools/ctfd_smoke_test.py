#!/usr/bin/env python3
"""End-to-end smoke test: plays GHOST VECTOR exactly like a player would.

It registers a throwaway player on your CTFd, downloads the challenge files
from CTFd, solves them with solutions/solve_all.py, submits every flag,
checks prerequisites and hint costs, then completes HANDSHAKE.SYS on the
terminal and submits the FINAL flag. Run it after importing the challenges
and before the event. Delete the "smoketest-..." user from CTFd afterwards.

Usage:
    python3 tools/ctfd_smoke_test.py \\
        --ctfd http://localhost:8000 \\
        --terminal http://localhost:8080 \\
        --coordinate GV-XXXX-0000          # your master coordinate

Needs: pip install requests pillow
Exit code 0 means every check passed.
"""

import argparse
import re
import secrets
import subprocess
import sys
import tempfile
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from build_ctfd import load_env  # noqa: E402

PASS, FAIL = "PASS", "FAIL"
results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(f"[{PASS if ok else FAIL}] {name}" + (f"  ({detail})" if detail else ""))
    return ok


class Player:
    def __init__(self, base):
        self.base = base.rstrip("/")
        self.s = requests.Session()
        self.nonce = None

    def _nonce(self, path="/challenges"):
        html = self.s.get(self.base + path).text
        m = re.search(r'csrfNonce.\s*[:=]\s*"([0-9a-f]+)"', html)
        self.nonce = m.group(1) if m else None

    def register(self):
        name = "smoketest-" + secrets.token_hex(3)
        html = self.s.get(self.base + "/register").text
        nonce = re.search(r'name="nonce"[^>]*value="([0-9a-f]+)"', html).group(1)
        r = self.s.post(self.base + "/register", data={
            "name": name, "email": name + "@example.com",
            "password": secrets.token_urlsafe(12), "nonce": nonce})
        self._nonce()
        return name, r.status_code in (200, 302)

    def api(self, method, path, **kw):
        h = {"CSRF-Token": self.nonce, "Content-Type": "application/json"}
        return self.s.request(method, self.base + "/api/v1" + path, headers=h, **kw).json()

    def challenges(self):
        return {c["name"]: c for c in self.api("GET", "/challenges")["data"]}

    def download(self, chal_id, dest):
        files = self.api("GET", f"/challenges/{chal_id}")["data"]["files"]
        for f in files:
            name = f.split("?")[0].split("/")[-1]
            (dest / name).write_bytes(self.s.get(self.base + f).content)
        return len(files)

    def submit(self, chal_id, flag):
        return self.api("POST", "/challenges/attempt",
                        json={"challenge_id": chal_id, "submission": flag})["data"]["status"]

    def score(self):
        return self.api("GET", "/users/me")["data"]["score"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ctfd", required=True)
    ap.add_argument("--terminal", required=True)
    ap.add_argument("--coordinate", required=True, help="master coordinate from your slate card")
    ap.add_argument("--env", default=str(ROOT / "config" / "flags.env"))
    a = ap.parse_args()
    env = load_env(a.env)

    p = Player(a.ctfd)
    name, ok = p.register()
    check("register throwaway player", ok, name)

    chals = p.challenges()
    phase1 = ["G1 Power Loss", "G2 Clock Drift", "G3 Thermal Whisper"]
    phase2 = ["V1 SYNC", "V2 VECTOR", "V3 COORD", "V4 PRIME"]
    check("Phase 1 visible at start", all(n in chals for n in phase1))
    check("Phase 2 and FINAL hidden at start",
          not any(n in chals for n in phase2 + ["FINAL Bring It Home"]), f"{len(chals)} visible")

    tmp = Path(tempfile.mkdtemp())
    p.download(chals["G1 Power Loss"]["id"], tmp)
    check("download ghost_telemetry.csv from CTFd", (tmp / "ghost_telemetry.csv").exists())

    check("wrong flag rejected", p.submit(chals["G1 Power Loss"]["id"], "AstroSec{nope}") == "incorrect")

    # Solve Phase 1 from the downloaded file, then unlock Phase 2
    check("G1 correct", p.submit(chals["G1 Power Loss"]["id"], env["FLAG_G1"]) == "correct")
    # Hints: first is free, second costs 10 percent (CTFd needs enough points)
    detail = p.api("GET", f"/challenges/{chals['G2 Clock Drift']['id']}")["data"]
    hints = detail.get("hints", [])
    check("G2 has 3 hints", len(hints) == 3)
    before = p.score()
    free = p.api("POST", "/unlocks", json={"target": hints[0]["id"], "type": "hints"})
    check("first hint is free", free.get("success") and p.score() == before)
    p.api("POST", "/unlocks", json={"target": hints[1]["id"], "type": "hints"})
    hint_cost = before - p.score()
    check("paid hint deducts points", hint_cost == 20, f"cost {hint_cost}")

    chals = p.challenges()
    check("Phase 2 unlocks after G1", all(n in chals for n in phase2))
    check("FINAL still hidden", "FINAL Bring It Home" not in chals)
    p.download(chals["V1 SYNC"]["id"], tmp)
    p.download(chals["V3 COORD"]["id"], tmp)
    check("Phase 2 files download after G1",
          (tmp / "vector_telemetry.csv").exists() and (tmp / "starmap.png").exists())

    out = subprocess.run([sys.executable, str(ROOT / "solutions" / "solve_all.py"), str(tmp)],
                         capture_output=True, text=True, cwd=tmp).stdout
    solved = dict(line.split(" ", 1) for line in out.strip().splitlines() if " " in line)
    check("solver recovers G1 from CTFd file", solved.get("G1") == env["FLAG_G1"])
    check("solver recovers G2 from CTFd file", solved.get("G2") == env["FLAG_G2"])
    check("solver recovers G3 from CTFd file", solved.get("G3") == env["FLAG_G3"])
    check("solver recovers V1", solved.get("V1") == env["CODE_V1"])
    check("solver recovers V2", solved.get("V2") == env["CODE_V2"])
    check("solver recovers V4", solved.get("V4") == env["CODE_V4"])
    check("starmap reveal written for V3", (tmp / "starmap_revealed.png").exists())

    for n, f in [("G2 Clock Drift", solved.get("G2")), ("G3 Thermal Whisper", solved.get("G3")),
                 ("V1 SYNC", solved.get("V1")), ("V2 VECTOR", "AstroSec{" + str(solved.get("V2")) + "}"),
                 ("V3 COORD", env["CODE_V3"].lower()), ("V4 PRIME", solved.get("V4"))]:
        check(f"{n} accepted by CTFd", p.submit(chals[n]["id"], f) == "correct")

    chals = p.challenges()
    check("FINAL unlocks after V1 to V4", "FINAL Bring It Home" in chals)

    # Final stage on the terminal
    t = requests.Session()
    term = a.terminal.rstrip("/")
    check("terminal is up", t.get(term + "/health").ok)
    t.post(term + "/api/uplink", json={"flag": env["FLAG_G1"]})
    hs = t.post(term + "/api/handshake", json={"codes": [env["CODE_V1"], env["CODE_V2"],
                                                          env["CODE_V3"], env["CODE_V4"]]}).json()
    check("HANDSHAKE.SYS locks all four markers", hs.get("ok") is True)
    tx = t.post(term + "/api/transmit", json={"coordinate": a.coordinate}).json()
    check("master coordinate accepted", tx.get("ok") is True, tx.get("message", "")[:60])
    final_flag = tx.get("flag")
    check("terminal reveals FINAL flag", bool(final_flag))
    if final_flag:
        check("FINAL accepted by CTFd", p.submit(chals["FINAL Bring It Home"]["id"], final_flag) == "correct")

    total = 2050 - hint_cost
    check("final score is correct", p.score() == total, f"{p.score()} of {total}")

    passed = sum(results)
    print(f"\n{passed}/{len(results)} checks passed. Remember to delete user {name} in CTFd.")
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
