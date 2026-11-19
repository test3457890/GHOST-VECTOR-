# Architecture

## With CTFd (recommended)

```
config/flags.env ──┬──► tools/build_ctfd.py ──► ctfd/build/*/challenge.yml + files ──► CTFd (ctfcli)
                   │            (runs the same generator, same SEED = identical files)
                   └──► Docker terminal ──► generator.py ──► /app/data
                                         └─► HANDSHAKE.SYS ──► reveals FLAG_FINAL ──► player submits to CTFd
```

CTFd owns accounts, flag checks, hints, prerequisites and the scoreboard. The terminal owns the story and the judge-verified final stage.

## Terminal internals

```
Browser ──> Flask app (gunicorn, port 8080)
              │
              ├── /                  Phase 1 briefing, ghost_telemetry.csv
              ├── /api/uplink        Phase 1 flag check, unlocks Phase 2 in the session
              ├── /vector            Phase 2 briefing, vector_telemetry.csv, starmap.png
              ├── /handshake         HANDSHAKE.SYS page
              ├── /api/handshake     Checks the four marker codes (SHA256 only)
              └── /api/transmit      Checks the master coordinate against PRIZE_KEY_HASH

Container first boot:
  entrypoint.sh ──> generator.py ──> /app/data (Docker volume)
                                      ghost_telemetry.csv
                                      vector_telemetry.csv
                                      starmap.png
                                      .hashes.json  (never served)
```

## Design notes

- **No plaintext answers in the app.** The generator writes SHA256 hashes of the flags and codes. The web app compares hashes with `hmac.compare_digest`.
- **The final rule is offline.** The master coordinate is built from a printed slate card. Only its hash is configured.
- **Slows brute force.** Every check endpoint adds a short delay.
- **Reproducible.** The same `SEED` and flags always produce the same files, so the staff solver can be checked before an event.
- **Unprivileged container.** The app runs as a non-root `ctf` user.
