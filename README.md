# GHOST VECTOR CTF

> **Prototype / proof-of-concept demo by Stuff Studios.** Built for AstroSec training events. This isn't a hardened production service.

GHOST VECTOR is a space-themed Capture The Flag challenge that runs in Docker. It merges two earlier AstroSec builds into one storyline:

- **Phase 1, Ghost Signal** (formerly *Ghost Satellite*): data forensics on a corrupted satellite telemetry dump. Three hidden flags.
- **Phase 2, Silent Vector** (formerly *Project Silent Vector*): four navigation marker codes hidden across a radio log and a star map.
- **Final stage, HANDSHAKE.SYS**: players lock in the four markers, get verified by a judge, and use a **physical alignment slate** to build a master coordinate. The rule on the slate never exists in any file, so a player can't finish by handing the files to an AI tool.

## Quick start

Requirements: Docker with the Compose plugin (any Linux, macOS or Windows host).

```bash
git clone <this repo>
cd ghost-vector-ctf
./setup.sh
```

Then open **http://localhost:8080**.

`setup.sh` creates `config/flags.env` from the example on first run. **Edit it before a real event.** See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

Stop it with `docker compose down`.

## Challenge overview

| ID | Phase | Skill | Points (suggested) |
|----|-------|-------|--------------------|
| G1 | Ghost Signal | CSV filtering, ASCII decoding | 100 |
| G2 | Ghost Signal | Time series analysis | 200 |
| G3 | Ghost Signal | LSB steganography in numeric data | 300 |
| V1 | Silent Vector | Pattern recognition | 150 |
| V2 | Silent Vector | Timing analysis, Morse code | 250 |
| V3 | Silent Vector | Image steganography | 200 |
| V4 | Silent Vector | Prime numbers, modular arithmetic | 350 |
| FINAL | Handshake | Judge verification plus physical slate | 500 |

## Learn with GHOST VECTOR

This repo is built for teaching. Start with the doc that fits you:

| Doc | Who it's for | Spoilers? |
|---|---|---|
| [Learning Guide](docs/LEARNING_GUIDE.md) | Players and instructors: the concepts, tools and practice exercises behind every challenge | No |
| [Player Briefing](docs/PLAYER_BRIEFING.md) | Players: the story, the rules and how to play | No |
| [Hint Book](docs/HINTS.md) | Players who are stuck: 3 hints per challenge, each one stronger | Light |
| [Walkthrough](docs/WALKTHROUGH.md) | After the event, or when you want to learn the full method | **Yes** |
| [Deployment Guide](docs/DEPLOYMENT.md) | Organizers: install, configure, launch, troubleshoot | No |
| [Architecture](docs/ARCHITECTURE.md) | Developers: how the app and generator fit together | No |

**Practice alone:** run `./setup.sh`, set `PHASE2_GATE=open` in `config/flags.env` to open both phases, and change `SEED` for a fresh puzzle. Check yourself with `solutions/solve_all.py` once you've had a go.

## Repository layout

```
ghost-vector-ctf/
  app/
    app.py               Flask recovery terminal
    generator.py         Builds all challenge data on first boot
    templates/           CRT terminal pages
    static/crt.css
    requirements.txt
  config/
    flags.example.env    Copy to flags.env (git ignored) and set real flags
  tools/
    set_prize_key.py     Hashes the master coordinate for the final stage
  extras/
    cosmolog_breadcrumb.html   Optional link from the CosmoLog platform
  docs/                  Learning guide, walkthrough, hints, briefing, deployment
  solutions/
    solve_all.py         Reference solver (spoilers)
  Dockerfile
  docker-compose.yml
  entrypoint.sh
  setup.sh
```

## Keeping answers secret

- Real flags live only in `config/flags.env`, which git ignores. No real flag is ever in this repo.
- The walkthrough and solver teach the **method**. They print whatever flags the running instance was built with.
- **Running a competitive event?** Players could read the walkthrough, so set new flags and a new `SEED`, and use the judge-verified final stage, which can't be solved from any file.
- The judge guide, event flag set and slate cards are kept in a separate staff package, outside this repo.

## License

MIT. See [LICENSE](LICENSE).
