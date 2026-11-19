# Deployment Guide

## 1. Install Docker (Ubuntu)

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-v2
sudo usermod -aG docker $USER
newgrp docker
docker compose version
```

If `docker compose` isn't found, `setup.sh` falls back to the older `docker-compose` automatically.

## 2. Configure flags

```bash
cp config/flags.example.env config/flags.env
nano config/flags.env
```

| Setting | What it does |
|---|---|
| `FLAG_G1`, `FLAG_G2`, `FLAG_G3` | Phase 1 flags in `AstroSec{...}` format |
| `CODE_V1` to `CODE_V4` | Phase 2 marker codes. `CODE_V2` may only use A to Z, 0 to 9 and `_` because it's sent as Morse |
| `FLAG_FINAL` | Flag shown on HANDSHAKE.SYS after a correct master coordinate, for players to submit to CTFd. Leave it blank for judge-only scoring |
| `PRIZE_KEY_HASH` | SHA256 of the master coordinate (step 3). Leave it blank and the final transmitter stays offline |
| `TERMINAL_URL` | The terminal's address as players will see it. It's used in the CTFd FINAL challenge |
| `SEED` | Changes where the data is hidden. Use a new seed for each event |
| `PHASE2_GATE` | `open` (default, best with CTFd) or `gated` (a Phase 1 flag submitted on the terminal unlocks Phase 2, for use without CTFd) |
| `SECRET_KEY` | Long random string used to sign sessions |
| `REGENERATE` | Set to `1` for one start to rebuild the data |
| `RATE_LIMIT`, `RATE_WINDOW` | Attempts allowed per client per window on each check endpoint (default 12 per 60 s) |
| `COOKIE_SECURE` | `1` when served over HTTPS, so the session cookie is HTTPS only |
| `TRUST_PROXY` | `1` when behind a reverse proxy (nginx, Caddy), so rate limits see the real client IP |

Flags are checked without regard to case.

## 3. Set the master coordinate

1. Decide the slate rule and write it on the alignment slate card (staff package).
2. Work out the master coordinate by hand from the four marker codes.
3. Run on a private machine:
   ```bash
   python3 tools/set_prize_key.py
   ```
4. Paste the printed `PRIZE_KEY_HASH=...` line into `config/flags.env`.

## 4. Launch

```bash
./setup.sh
```

Open `http://localhost:8080` (or `http://<host-ip>:8080` from other machines). To use another port, run `HOST_PORT=9000 ./setup.sh`.

## 5. Changing flags or seed later

Rebuild the CTFd pack too (`python3 tools/build_ctfd.py`, then `ctf challenge sync`), so the files players download match the terminal.


Challenge data is generated **once** and kept in a Docker volume. After you change flags or the seed:

```bash
docker compose down -v
docker compose up -d --build
```

## 6. Connect to CTFd

Follow [CTFD_SETUP.md](CTFD_SETUP.md) to build the challenge pack and import it.

## 7. Pre-event checklist

- [ ] `config/flags.env` has new flags, a new `SEED`, `FLAG_FINAL`, a secret key and a prize key hash
- [ ] Terminal reset after the config changes (`docker compose down -v && ./setup.sh`)
- [ ] CTFd pack rebuilt from the same config and imported
- [ ] `tools/ctfd_smoke_test.py` shows 32/32 checks passed, and the smoketest user is deleted
- [ ] `TERMINAL_URL/health` loads from a player machine on the event network
- [ ] Slate cards printed and handed to the judges

## Useful commands

| Task | Command |
|---|---|
| View logs | `docker logs -f ghost-vector-ctf` |
| Stop | `docker compose down` |
| Stop and wipe data | `docker compose down -v` |
| Copy data out for testing | `docker cp ghost-vector-ctf:/app/data ./data` |
| Health check | `curl localhost:8080/health` |

## Troubleshooting

| Problem | Fix |
|---|---|
| `permission denied` on docker.sock | Run `newgrp docker` or log out and back in |
| Changed flags but nothing changed | Run `docker compose down -v`, then rebuild |
| Final stage says transmitter offline | Set `PRIZE_KEY_HASH`, then run `docker compose up -d --force-recreate` |
| Phase 2 page sends you back to Phase 1 | Expected while gated. Submit a Phase 1 flag first, or set `PHASE2_GATE=open` |
| Port 8080 already in use | Run `HOST_PORT=9000 ./setup.sh` |
