# Running GHOST VECTOR on CTFd

> Prototype / proof-of-concept demo by Stuff Studios. Prefer pictures? See the [illustrated Setup Guide](SETUP_GUIDE.md). Tested end to end on **CTFd 3.8.9** with **ctfcli 0.1.8**, using both standard and dynamic scoring.

GHOST VECTOR runs in two parts:

| Part | What it does | Where |
|---|---|---|
| **CTFd** | Accounts, teams, challenge board, flag checking, hints, scoreboard | Your CTFd server |
| **Recovery terminal** | The story pages and **HANDSHAKE.SYS** (the judge-verified final stage) | This repo's Docker container |

Players download the challenge files from CTFd and submit every flag to CTFd. They only visit the terminal for the final stage.

```
 Player ──► CTFd ── G1 G2 G3 ──► unlocks V1 V2 V3 V4 ──► unlocks FINAL
                                                            │
                                     Recovery terminal ◄────┘
                                     HANDSHAKE.SYS ── judge ── slate card
                                            │
                                            └── reveals FINAL flag ──► CTFd
```

## The board

| Challenge | Category | Points | Unlocks after | Files |
|---|---|---|---|---|
| G1 Power Loss | Phase 1: Ghost Signal | 100 | always open | ghost_telemetry.csv |
| G2 Clock Drift | Phase 1: Ghost Signal | 200 | always open | ghost_telemetry.csv |
| G3 Thermal Whisper | Phase 1: Ghost Signal | 300 | always open | ghost_telemetry.csv |
| V1 SYNC | Phase 2: Silent Vector | 150 | G1 | vector_telemetry.csv |
| V2 VECTOR | Phase 2: Silent Vector | 250 | G1 | vector_telemetry.csv |
| V3 COORD | Phase 2: Silent Vector | 200 | G1 | starmap.png |
| V4 PRIME | Phase 2: Silent Vector | 350 | G1 | vector_telemetry.csv |
| FINAL Bring It Home | Final: Handshake | 500 | V1, V2, V3 and V4 | none (links to the terminal) |
| **Total** | | **2,050** | | |

- **Locked challenges are hidden** until their prerequisites are solved. Phase 2 appears after G1, and FINAL appears after all four markers.
- **Every flag is static and case insensitive.** Phase 2 accepts the bare code (`NAV_...`) or the wrapped form (`AstroSec{NAV_...}`).
- **Hints:** 3 per challenge. The first is free, the second costs 10% of the points and the third costs 25%. FINAL has no hints.

## Step 1: Configure your flags

```bash
cp config/flags.example.env config/flags.env
nano config/flags.env
```

Change **every** `CHANGE_ME` value, plus:

- `SEED`: any number. A new seed moves where everything is hidden.
- `FLAG_FINAL`: the flag the terminal shows after a correct master coordinate.
- `TERMINAL_URL`: the address players will use to reach the terminal, for example `http://10.0.0.5:8080`. It's written into the FINAL challenge text.
- `PHASE2_GATE=open`: CTFd already handles unlocking, so leave this open.

## Step 2: Set the final-stage coordinate

1. Write your combination rule on the alignment slate card (staff package).
2. Work out the master coordinate by hand.
3. Run `python3 tools/set_prize_key.py` and paste the printed `PRIZE_KEY_HASH=...` line into `config/flags.env`.

## Step 3: Start the terminal

```bash
./setup.sh
```

Check that `TERMINAL_URL/health` returns `{"status":"ok"}` from another machine on the event network.

## Step 4: Build the CTFd pack

```bash
pip install pyyaml pillow
python3 tools/build_ctfd.py             # standard scoring
python3 tools/build_ctfd.py --dynamic   # or dynamic scoring (points drop as more teams solve)
```

This creates `ctfd/build/`, which contains:

- one folder per challenge with a `challenge.yml` and its files
- `MANUAL_ENTRY.md`, a copy-paste sheet if you'd rather enter everything by hand

The files are generated with the **same flags and seed** as the terminal, so they match byte for byte. **`ctfd/build/` contains real flags and is git ignored. Never commit it.**

> Changed a flag or the seed? Rebuild the pack **and** reset the terminal (`docker compose down -v && ./setup.sh`) so both stay in sync.

## Step 5: Import into CTFd

### Option A: ctfcli (recommended, about 1 minute)

1. In CTFd, go to **Settings** (top right), then **Access Tokens**, and generate a token. Use an admin account.
2. Run:
   ```bash
   pip install ctfcli
   cd ctfd/build
   mkdir -p .ctf
   printf "[config]\nurl = https://YOUR-CTFD\naccess_token = YOUR_TOKEN\n\n[challenges]\n" > .ctf/config
   for d in 0*/; do ctf challenge install "$d"; done
   ```
3. Install them **in folder order** (the loop does this), because the Phase 2 and FINAL prerequisites refer to challenges that must already exist.
4. **Updating later:** change the flags, rebuild, then run `ctf challenge sync "$d"` in the same loop.

### Option B: by hand in the CTFd admin panel

For each challenge in `MANUAL_ENTRY.md`:

1. **Admin Panel > Challenges > +**. Choose **standard** (or **dynamic**).
2. Enter the name, category, description and points exactly as listed.
3. **Flags tab:** add each flag as **static** and **case insensitive**.
4. **Files tab:** upload the listed file from that challenge's `files/` folder.
5. **Hints tab:** add the 3 hints with their costs.
6. **Requirements tab:** add the prerequisites listed (Phase 2 needs G1; FINAL needs V1 to V4).
7. FINAL only: set **Connection Info** to your terminal's `/handshake` address.

## Step 6: Test like a player (do not skip)

```bash
pip install requests pillow
python3 tools/ctfd_smoke_test.py \
  --ctfd https://YOUR-CTFD \
  --terminal http://YOUR-TERMINAL:8080 \
  --coordinate YOUR-MASTER-COORDINATE
```

It registers a throwaway `smoketest-xxxxxx` player and runs **32 checks**: downloads files from CTFd, solves them, submits every flag, checks hidden and unlocked challenges, hint costs, a wrong flag, the full HANDSHAKE.SYS flow and the final score. **All 32 must pass.** Afterwards, delete the smoketest user in **Admin Panel > Users**.

## Step 7: Event day

- **Judges** get section 6 of the staff guide and the printed slate cards.
- **FINAL scoring:** a team that transmits the right coordinate sees the FINAL flag and submits it to CTFd. Because the slate only comes from a judge, every FINAL solve went through a judge.
- **Judge-only mode:** leave `FLAG_FINAL` blank and rebuild the pack. FINAL then has no flag, and judges award it in **Admin Panel > Submissions** by marking it correct for the team.

## Recommended CTFd settings

| Setting | Value | Why |
|---|---|---|
| Challenge visibility | Private (login required) | Files are only for registered players |
| User mode | Teams | 2 or 3 per team works best |
| Score visibility | Public | Live scoreboard |
| Max attempts per challenge | Unlimited, or 20 if you're worried about guessing | Flags are long enough that guessing isn't practical |
| Rate limiting | CTFd default | Already slows brute forcing |

## Troubleshooting

| Problem | Fix |
|---|---|
| `ctf challenge install` says a requirement wasn't found | Install in folder order: G1 first, FINAL last |
| A correct flag is marked wrong | The pack and terminal were built with different flags or seeds. Rebuild both from the same `config/flags.env` |
| A player can't see Phase 2 | Expected until G1 is solved |
| FINAL has no flag | `FLAG_FINAL` was blank when you built the pack. Judges award it by hand, or set it and run `ctf challenge sync` |
| The terminal says "transmitter offline" | `PRIZE_KEY_HASH` is blank. Set it and run `docker compose up -d --force-recreate` |
| A smoke test check fails | Read the line marked FAIL. Most failures are a flag or seed mismatch |
