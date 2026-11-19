# GHOST VECTOR CTF

[![CI](https://github.com/test3457890/GHOST-VECTOR-/actions/workflows/ci.yml/badge.svg)](https://github.com/test3457890/GHOST-VECTOR-/actions/workflows/ci.yml)

> **Prototype / proof-of-concept demo by Stuff Studios.** Built for AstroSec training events and classrooms. This isn't a hardened production service.

**New here? Start with the [illustrated Setup Guide](docs/SETUP_GUIDE.md).**

![HANDSHAKE.SYS final stage](docs/images/terminal-handshake-locked.png)

GHOST VECTOR is a space-themed Capture The Flag event built for **CTFd**. A lost satellite, **GHOST-01**, has woken up and is broadcasting corrupted telemetry. Players work through three phases:

1. **Phase 1, Ghost Signal:** three flags hidden in a satellite telemetry CSV (data forensics, timing, LSB steganography).
2. **Phase 2, Silent Vector:** four navigation markers hidden in a radio log and a star map (pattern recognition, Morse timing, image steganography, primes and modular arithmetic).
3. **Final, HANDSHAKE.SYS:** players lock in their markers, explain their methods to a **judge**, get a **printed alignment slate**, and build the master coordinate by hand. The rule exists only on paper, so a player can't finish by handing the files to an AI tool.

## Is it tested?

Yes. Every push runs the [CI workflow](.github/workflows/ci.yml):

- **Security scans:** bandit, pip-audit, a Trivy image scan, a spoiler guard, and a live check that the container is hardened. See [docs/SECURITY.md](docs/SECURITY.md).
- **52 unit tests:** the generator, the terminal (including security headers, rate limits and input caps), the CTFd pack builder and the repo rules.
- **End to end:** builds the Docker image, starts a real **CTFd**, imports all 8 challenges with ctfcli, then plays the whole CTF as a player. That covers downloading the files from CTFd, solving them, submitting every flag, checking that locked challenges unlock, checking hint costs, doing HANDSHAKE.SYS and checking the final score. **32 checks, all passing.**

You can run the same player test against your own CTFd before an event. See [docs/TESTING.md](docs/TESTING.md).

## The challenges

| ID | Category | Skill | Points | Unlocks after |
|----|----------|-------|--------|---------------|
| G1 Power Loss | Phase 1 | Filtering data, ASCII | 100 | always open |
| G2 Clock Drift | Phase 1 | Time series deltas | 200 | always open |
| G3 Thermal Whisper | Phase 1 | LSB steganography | 300 | always open |
| V1 SYNC | Phase 2 | Pattern recognition | 150 | G1 |
| V2 VECTOR | Phase 2 | Timing analysis, Morse | 250 | G1 |
| V3 COORD | Phase 2 | Image steganography | 200 | G1 |
| V4 PRIME | Phase 2 | Primes, modular arithmetic | 350 | G1 |
| FINAL Bring It Home | Final | Explaining your method to a judge | 500 | V1 to V4 |

**2,050 points in total.** Each challenge has 3 hints (the first is free, the second costs 10% and the third costs 25%).

## Quick start for organizers (CTFd)

```bash
git clone https://github.com/test3457890/GHOST-VECTOR-.git
cd GHOST-VECTOR-
cp config/flags.example.env config/flags.env   # then change every CHANGE_ME value
python3 tools/set_prize_key.py                  # paste the hash into config/flags.env
./setup.sh                                      # starts the recovery terminal on :8080
python3 tools/build_ctfd.py                     # builds the CTFd challenge pack
cd ctfd/build && mkdir -p .ctf && printf "[config]\nurl = https://YOUR-CTFD\naccess_token = YOUR_TOKEN\n\n[challenges]\n" > .ctf/config
for d in 0*/; do ctf challenge install "$d"; done
cd ../.. && python3 tools/ctfd_smoke_test.py --ctfd https://YOUR-CTFD --terminal http://YOUR-HOST:8080 --coordinate YOUR-COORDINATE
```

Step by step with screenshots: **[docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)**. Entering challenges by hand without ctfcli: **[docs/CTFD_SETUP.md](docs/CTFD_SETUP.md)**.

## Learn with GHOST VECTOR

| Doc | Who it's for | Spoilers? |
|---|---|---|
| [Learning Guide](docs/LEARNING_GUIDE.md) | Players and instructors: concepts, tools, practice exercises | No |
| [Player Briefing](docs/PLAYER_BRIEFING.md) | Players: story, rules, how to play | No |
| [Hint Book](docs/HINTS.md) | Players who are stuck: 3 hints per challenge | Light |
| Walkthrough and solver | Instructors and staff: inside the encrypted staff pack (see below) | **Yes** |

**Practice alone without CTFd:** run `./setup.sh` and open `http://localhost:8080`. Phase 1 and 2 files download straight from the terminal.

## Organizer docs

| Doc | What's in it |
|---|---|
| [Setup Guide](docs/SETUP_GUIDE.md) | **Start here.** Every step with screenshots |
| [CTFd Setup](docs/CTFD_SETUP.md) | Build the pack, import it, recommended CTFd settings, event day |
| [Security](docs/SECURITY.md) | What is locked down and how it's tested |
| [Deployment](docs/DEPLOYMENT.md) | Docker install, every config setting, troubleshooting |
| [Testing](docs/TESTING.md) | Unit tests, CI, the pre-event player smoke test |
| [Architecture](docs/ARCHITECTURE.md) | How the generator, terminal and CTFd fit together |

## Repository layout

```
GHOST-VECTOR-/
  app/                    Recovery terminal (Flask) and challenge data generator
  config/
    flags.example.env     Copy to flags.env (git ignored) and set real flags
  tools/
    build_ctfd.py         Builds the ctfcli challenge pack from your flags
    ctfd_smoke_test.py    Plays the whole CTF against your CTFd (32 checks)
    set_prize_key.py      Hashes the master coordinate for the final stage
    staff_vault.py        Unlocks and locks the encrypted staff pack
  staff/
    ghost-vector-staff.7z AES-256 encrypted: walkthrough, solver, judge guide, flags
  tests/                  pytest suite and CI helpers
  docs/                   Learning guide, walkthrough, hints, CTFd setup and more
  extras/                 Optional CosmoLog breadcrumb
  .github/workflows/      CI: unit tests plus Docker and real CTFd end to end
  Dockerfile, docker-compose.yml, entrypoint.sh, setup.sh
```

## Keeping answers locked up

- **No real flag is ever in this repo.** Flags live only in `config/flags.env` and `ctfd/build/`, and git ignores both.
- **All spoilers are encrypted.** The walkthrough, solver, judge guide, slate card and a tested flag set live only in `staff/ghost-vector-staff.7z` (AES-256 with encrypted file names). Open it with `python3 tools/staff_vault.py unlock` or with 7-Zip. Older plain-text copies were scrubbed from the git history.
- **CI enforces it:** the build fails if a spoiler or a flags file is ever committed in plain text.

## License

MIT. See [LICENSE](LICENSE).
