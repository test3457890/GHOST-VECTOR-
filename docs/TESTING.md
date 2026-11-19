# Testing

GHOST VECTOR is tested at three levels. All of them run on every push in [GitHub Actions](../.github/workflows/ci.yml).

## 1. Unit tests (41 tests, about 3 seconds)

```bash
pip install -r requirements-dev.txt
python3 -m pytest -v
```

| File | What it proves |
|---|---|
| `tests/test_generator.py` | The same seed always gives identical files, a new seed changes them, and every flag can be solved across many seeds and flag sets. Flags never appear in plain text in player files, and the V3 text is really hidden |
| `tests/test_app.py` | Every terminal route works: Phase 2 locking, wrong or right uplinks, flags not case sensitive, wrapped codes, path traversal and hash-file downloads blocked, partial handshakes, the full final stage, offline mode, judge-only mode, and no flags in any page |
| `tests/test_build_ctfd.py` | The CTFd pack has 8 challenges in order, 2,050 points, the right flags, prerequisites and hint costs. Its files match the terminal byte for byte, and dynamic mode and config validation work |
| `tests/test_repo.py` | No em or en dashes in tracked files, `config/flags.env` is never committed, and the example config is valid |

## 2. End to end in CI (real Docker plus real CTFd)

The `end-to-end` CI job:

1. Builds the Docker image and starts the terminal with `./setup.sh`.
2. Starts a blank `ctfd/ctfd:latest` container and runs first-time setup.
3. Builds the challenge pack, then lints and installs all 8 challenges with ctfcli.
4. Runs the player smoke test below.

## 3. Player smoke test (run this before every event)

```bash
pip install requests pillow
python3 tools/ctfd_smoke_test.py --ctfd https://YOUR-CTFD --terminal http://YOUR-TERMINAL:8080 --coordinate YOUR-COORDINATE
```

It registers a throwaway player and runs **32 checks**:

- Phase 1 is visible, and Phase 2 and FINAL are hidden at the start
- files download from CTFd, a wrong flag is rejected, and G1 is accepted
- the first hint is free and the second costs points
- Phase 2 unlocks after G1, and FINAL stays hidden
- the reference solver recovers G1, G2, G3, V1, V2 and V4 **from the files CTFd serves**, and V3's reveal image is produced
- every flag is accepted by CTFd (including the wrapped and lower-case forms)
- FINAL unlocks after V1 to V4
- the terminal is up, HANDSHAKE.SYS locks all four markers, the master coordinate is accepted and the FINAL flag is revealed
- CTFd accepts FINAL, and the final score is exactly 2,050 minus the hint cost

Exit code 0 means everything passed. Delete the `smoketest-xxxxxx` user from CTFd afterwards.

## Verified versions

| Component | Version |
|---|---|
| CTFd | 3.8.9 (standard and dynamic scoring) and `ctfd/ctfd:latest` in CI |
| ctfcli | 0.1.8 |
| Python | 3.11 to 3.13 |
| Docker base image | python:3.12-slim |
