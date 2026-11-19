# Changelog

## 2.1.0 (2026-11-18)

- **Locked up:** the walkthrough, solver, judge guide, slate card and tested flags are now stored only in `staff/ghost-vector-staff.7z` (AES-256, encrypted file names). `tools/staff_vault.py` unlocks and locks it. The plain-text copies and the tested marker codes were scrubbed from the git history.
- **Hardened terminal:** a strict CSP with no inline script, security headers, per-client rate limits, JSON-only APIs with size and input caps, HttpOnly and SameSite=Strict cookies, weak-key protection, and JSON error pages.
- **Hardened container:** read-only filesystem, all capabilities dropped, no-new-privileges, memory, process and CPU caps, pinned and audited dependencies (Pillow 13.0.0).
- **CI security job:** bandit, pip-audit, a Trivy image scan, a spoiler guard and a live hardening check.
- **Illustrated Setup Guide** with 16 real screenshots, plus a new Security doc.
- The example config now uses placeholder marker codes (`NAV_CHANGEME_...`).
- 52 unit tests. Solver tests skip while the staff pack is locked.

## 2.0.0 (2026-11-18)

- **CTFd integration:** `tools/build_ctfd.py` builds a ctfcli pack (8 challenges, hints with costs, prerequisites, files, optional dynamic scoring) and a manual entry sheet.
- **FINAL is scoreable in CTFd:** HANDSHAKE.SYS reveals `FLAG_FINAL` after a correct master coordinate. Leave it blank for judge-only scoring.
- **Player smoke test:** `tools/ctfd_smoke_test.py` plays the whole CTF against a live CTFd (32 checks).
- **41-test pytest suite** and **GitHub Actions CI**, which builds the Docker image, imports into a real CTFd and plays it end to end.
- `PHASE2_GATE` now defaults to `open`, because CTFd handles unlocking.
- New docs: CTFd Setup and Testing. Updated README, Deployment, Architecture, Player Briefing, Hints and Walkthrough.

## 1.1.0 (2026-11-18)

- Added the Learning Guide: concepts, tools, practice exercises, learning path and instructor notes.
- Added the full Walkthrough with tested code for every challenge.
- Added the reference solver in `solutions/`.
- README now has a docs table and practice-mode instructions.

## 1.0.0 (2026-11-13)

- Merged Ghost Satellite and Project Silent Vector into one app, GHOST VECTOR.
- Ghost Satellite's three tiers are now all active at once as G1, G2 and G3 (previously one tier at a time).
- Silent Vector's four tiers are kept as V1 to V4, with the judge and slate final stage.
- Phase 2 unlocks once any Phase 1 flag is submitted (set `PHASE2_GATE=open` to skip the gate).
- All flags now come from `config/flags.env`. No real flag is in the source code.
- Marker codes and the master coordinate are checked against SHA256 hashes only.
- One port (8080), one container, one setup script.
