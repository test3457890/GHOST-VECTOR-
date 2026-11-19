# Uploading to GitHub

## Option A: GitHub website (no command line)

1. Go to github.com, click **New repository**, name it `ghost-vector-ctf` and set it to **Private**.
2. Don't add a README (this repo already has one).
3. Click **uploading an existing file**, drag in everything **inside** the `ghost-vector-ctf` folder and commit.
4. Note: the website can hide dotfiles. Make sure `.gitignore` and `.dockerignore` were uploaded. If not, create them with **Add file > Create new file** and paste in their contents.

## Option B: command line

```bash
cd ghost-vector-ctf
git init
git add .
git commit -m "GHOST VECTOR CTF v1.0.0"
git branch -M main
git remote add origin https://github.com/<your-user>/ghost-vector-ctf.git
git push -u origin main
```

Or with the GitHub CLI:

```bash
gh repo create ghost-vector-ctf --private --source . --push
```

## Never upload

- `config/flags.env`
- Anything from the `staff-private` package (solvers, staff guide, slate card, event flags)

## Suggested repo settings

- **About:** "Space-themed CTF prototype: telemetry forensics, steganography, Morse and prime puzzles with a judge-verified final stage."
- **Topics:** `ctf`, `cybersecurity`, `steganography`, `flask`, `docker`, `education`
- Turn on the **Wiki** if you want to mirror the docs folder there.
