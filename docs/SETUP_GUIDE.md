# GHOST VECTOR Setup Guide (with screenshots)

> Prototype / proof-of-concept demo by Stuff Studios. Every screenshot below was taken from a real run of this repo on CTFd 3.8.9, using the **example placeholder flags** (`CHANGE_ME`). Your own flags won't appear anywhere public.

**Time needed:** about 30 minutes the first time.
**You need:** a Linux machine or VM with Docker, Python 3.10 or newer, and a CTFd server (an existing one, or one you start yourself).

---

## Step 1: Get the code

```bash
git clone https://github.com/test3457890/GHOST-VECTOR-.git
cd GHOST-VECTOR-
pip install -r requirements-dev.txt ctfcli
```

## Step 2: Set your flags

```bash
cp config/flags.example.env config/flags.env
nano config/flags.env
```

- Replace **every** `CHANGE_ME` and `CHANGEME` value with your own flags and marker codes.
- Set `SEED` to any new number.
- Set `SECRET_KEY` to a long random string: `python3 -c "import secrets; print(secrets.token_hex(32))"`
- Set `TERMINAL_URL` to the address players will use, for example `http://10.0.0.5:8080`.

`config/flags.env` is **git ignored**, so it can never be pushed by accident.

## Step 3: Set the final-stage coordinate

1. Decide your slate rule (the staff pack has an example card).
2. Work out the master coordinate by hand.
3. Run:
   ```bash
   python3 tools/set_prize_key.py
   ```
4. Paste the printed `PRIZE_KEY_HASH=...` line into `config/flags.env`.

## Step 4: Start the recovery terminal

```bash
./setup.sh
```

Open `http://YOUR-HOST:8080`. You should see the Phase 1 page:

![Recovery terminal, Phase 1](images/terminal-phase1.png)

And the Phase 2 page:

![Recovery terminal, Phase 2](images/terminal-phase2.png)

The container runs **hardened**: read-only filesystem, no Linux capabilities, non-root user, and memory and process limits. See [SECURITY.md](SECURITY.md).

## Step 5: Prepare CTFd

**New CTFd?** Start one with `docker run -d -p 8000:8000 ctfd/ctfd`, open it and complete the setup wizard. Use **Teams** mode for an event.

![CTFd setup wizard](images/ctfd-setup.png)

**Create an admin access token:** go to **Settings**, then **Access Tokens**, and click **Generate**. Copy the token: it's only shown once.

![CTFd access tokens](images/ctfd-access-tokens.png)

## Step 6: Build and import the challenges

```bash
python3 tools/build_ctfd.py            # or add --dynamic for decaying points
cd ctfd/build
mkdir -p .ctf
printf "[config]\nurl = https://YOUR-CTFD\naccess_token = YOUR_TOKEN\n\n[challenges]\n" > .ctf/config
for d in 0*/; do ctf challenge install "$d"; done
cd ../..
```

![Importing with ctfcli](images/ctfcli-install.png)

In **Admin Panel > Challenges** you should now see all 8:

![CTFd admin challenge list](images/ctfd-admin-challenges.png)

The prerequisites are set automatically. Phase 2 needs G1, and FINAL needs all four markers:

![V1 SYNC requires G1](images/ctfd-admin-requirements.png)

> `ctfd/build/` contains your real flags. It is git ignored. Delete it after importing if you're on a shared machine.

## Step 7: Run the pre-event test (do not skip)

```bash
python3 tools/ctfd_smoke_test.py --ctfd https://YOUR-CTFD --terminal http://YOUR-HOST:8080 --coordinate YOUR-COORDINATE
```

![Smoke test, 32 of 32 passing](images/smoke-test.png)

- **All checks must pass.** The 7 "solver" checks need the unlocked staff pack (Step 10). Without it they show as SKIP, and the other 25 still test CTFd fully.
- Afterwards, delete the `smoketest-xxxxxx` user in **Admin Panel > Users**.

## Step 8: What players see

At the start, only Phase 1 is visible:

![Player board at start](images/player-board-start.png)

Each challenge has the story, the file to download and 3 hints (free, then 10%, then 25% of the points):

![G1 challenge](images/player-challenge-g1.png)

A correct flag:

![Correct flag](images/player-flag-correct.png)

Solving G1 unlocks Phase 2:

![Phase 2 unlocked](images/player-board-phase2.png)

## Step 9: The final stage (judge plus terminal)

When all four markers are solved, FINAL appears. The team opens **HANDSHAKE.SYS** and locks in the four markers:

![Markers locked](images/terminal-handshake-locked.png)

The team goes to a **judge**, explains how they found each marker (staff guide, section 6), and gets the **alignment slate**. They build the master coordinate and transmit it, and the terminal shows the FINAL flag:

![Final flag revealed](images/terminal-final-flag.png)

They submit it to CTFd. A full clear looks like this:

![All challenges solved](images/player-board-complete.png)

![Scoreboard](images/ctfd-scoreboard.png)

## Step 10: Open the encrypted staff pack

The walkthrough, solver, judge guide, slate card and a tested flag set are stored in the repo **only** as an AES-256 encrypted file: `staff/ghost-vector-staff.7z`.

```bash
python3 tools/staff_vault.py unlock     # asks for the password, creates staff-unlocked/
python3 tools/staff_vault.py lock       # after editing, re-encrypt
python3 tools/staff_vault.py lock --new-password   # change the password
```

- **No Python?** Open the `.7z` with **7-Zip** (Windows), **Keka** (macOS) or **p7zip** (Linux) and enter the password.
- `staff-unlocked/` is git ignored. Delete it when you're done: `rm -rf staff-unlocked`

## Step 11 (optional): Let GitHub run the full tests

CI already runs on every push. To also run the solver checks there, give CI the staff pack password:

1. On GitHub, open the repo, then **Settings > Secrets and variables > Actions**.
2. Click **New repository secret**.
3. Name: `STAFF_PACK_PASSWORD`. Value: your staff pack password.
4. Save. The next CI run unlocks the pack inside the runner, runs everything, and never prints the password.

## Event-day checklist

- [ ] New flags, marker codes, `SEED`, `SECRET_KEY` and `FLAG_FINAL` in `config/flags.env`
- [ ] `PRIZE_KEY_HASH` set from your slate rule
- [ ] Terminal reset after config changes: `docker compose down -v && ./setup.sh`
- [ ] CTFd pack rebuilt from the same config and imported
- [ ] Smoke test passing, and the smoketest user deleted
- [ ] Slate cards printed, judges briefed (staff guide, section 6)
- [ ] `staff-unlocked/` and `ctfd/build/` deleted from any shared machine

Stuck? See [CTFD_SETUP.md](CTFD_SETUP.md#troubleshooting) and [DEPLOYMENT.md](DEPLOYMENT.md#troubleshooting).
