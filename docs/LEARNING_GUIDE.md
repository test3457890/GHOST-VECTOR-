# Learning Guide

GHOST VECTOR is built to **teach**, not just to score. This guide explains the skills behind every challenge, the tools to use and how to practice. It contains **no flags and no direct answers**. For the full solutions, see [WALKTHROUGH.md](WALKTHROUGH.md) (spoilers).

> Prototype / proof-of-concept demo by Stuff Studios.

## Who this is for

- **Beginners:** students who know a little Python or can use a spreadsheet.
- **Intermediate players:** people who want practice with data forensics and steganography.
- **Instructors:** anyone running a class or club session (see the end of this guide).

## What you will learn

| Challenge | Core skill | Real-world use |
|---|---|---|
| G1 Power Loss | Filtering data, ASCII encoding | Spotting impossible values in sensor logs |
| G2 Clock Drift | Time series deltas | Finding timing covert channels and log tampering |
| G3 Thermal Whisper | Least significant bit (LSB) steganography | Detecting data hidden in "noise" |
| V1 SYNC | Pattern recognition | Signal analysis, beaconing detection |
| V2 VECTOR | Timing analysis, Morse code | Covert timing channels in network traffic |
| V3 COORD | Image steganography | Digital forensics on images |
| V4 PRIME | Prime numbers, modular arithmetic | The maths behind cryptography (RSA, hashing) |
| FINAL | Explaining your method | Writing up and defending findings, like a real analyst |

## Set up your toolkit

You can solve everything with free tools. Pick one path.

**Path A: Python (recommended)**

```bash
python3 -m pip install pandas pillow sympy
```

- **pandas** reads and filters CSV files.
- **Pillow** opens and edits images.
- **sympy** has a ready-made `isprime()` function.

**Path B: no coding**

- **Spreadsheet:** Excel, Google Sheets or LibreOffice Calc (`=CHAR()`, filters, formulas).
- **CyberChef** (gchq.github.io/CyberChef): decodes binary, Morse, Base64 and more.
- **GIMP** (free image editor): Levels and Curves for image stego.

## Core concepts

### 1. ASCII: numbers that are really letters
Computers store each character as a number. `A` is 65, `a` is 97, `{` is 123. If you see a column of whole numbers between 32 and 126 where they don't belong, try converting them to characters.

- **Python:** `chr(65)` gives `"A"`, and `ord("A")` gives `65`.
- **Spreadsheet:** `=CHAR(65)`.
- **Practice:** decode `72 105 33`.

### 2. Anomalies: what doesn't belong
Real sensor data follows patterns. A satellite battery drifts slowly. It doesn't drop to exactly 0 and bounce back. Learn to ask: **"Which values are physically impossible?"**

- Sort each column and look at the smallest and largest values.
- Plot a column, because a spike is easy to see on a chart.
- Count how often each value appears (`value_counts()` in pandas).

### 3. Time series and deltas
Sometimes the message isn't in the values but in **when** they happen. The difference between one timestamp and the next is called a **delta**.

- **pandas:** `pd.to_datetime(df.Timestamp).diff()`
- If almost every delta is the same, the odd ones out are your signal.
- **Real world:** attackers hide data in packet timing ("covert timing channels").

### 4. Bits and the least significant bit (LSB)
Every whole number is stored as bits. The **last bit** (the LSB) decides whether a number is odd or even. Changing it moves the value by only 1, so nobody notices. That makes it a classic hiding place.

- `n & 1` gives the LSB of `n` (0 = even, 1 = odd).
- **8 bits make 1 byte**, and 1 byte can be 1 ASCII character.
- **Decimals:** if a value has 3 decimal places, multiply by 1000 first to get a whole number.
- **Practice:** the bits `01001000 01101001` spell a word. Decode them in CyberChef ("From Binary").

### 5. Signal frequencies
In radio, a **frequency** is like a channel. One frequency showing up again and again with the *exact* same value is a sign that someone placed it on purpose.

- **Fun fact:** 1420.405 MHz is the **hydrogen line**, the frequency radio astronomers use to map the galaxy.

### 6. Morse code
Morse turns letters into short and long signals (dots and dashes) separated by pauses.

- `SOS` is `... --- ...`
- Short versus long can be **sounds, flashes or time gaps**.
- **Practice:** decode `.... . .-.. .-.. ---`.

### 7. Image steganography
A pixel is three numbers: red, green and blue, each from 0 to 255. Black is `(0,0,0)`. A pixel at `(1,1,1)` looks **exactly** black to a human eye, but a computer can tell the difference.

- **GIMP:** Colors, then Levels, and drag the white point all the way left.
- **Python:** turn every pixel that isn't pure black into white.
- **Tools:** Stegsolve, Aperi'Solve, `zsteg` (for PNG LSB stego).

### 8. Primes and modular arithmetic
- A **prime** can only be divided by 1 and itself: 2, 3, 5, 7, 11, 13...
- **Modulo** (`%`) gives the remainder: `130 % 127 = 3`.
- Modulo "wraps" big numbers into a smaller range, which is how a large number can be turned into an ASCII code.
- **Real world:** RSA encryption is built on primes and modular arithmetic.
- **Practice:** which of these are prime: 91, 97, 127, 129?

## How to approach any data challenge

1. **Read the story.** Every hint in the briefing points at a column or a technique.
2. **Look before you code.** Open the file and scroll through it. Sort the columns.
3. **Find the odd one out.** Impossible values, repeats, gaps, extra precision.
4. **Form a guess and test it fast.** Convert to ASCII and see if it looks like text.
5. **Write down what worked.** You'll need to explain it to a judge, and to yourself next time.

## Learning path

| Level | Do these | Focus |
|---|---|---|
| 1 | G1, V1 | Filtering and ASCII |
| 2 | G2, V3 | Timing and images |
| 3 | V2 | Combining timing with Morse |
| 4 | G3, V4 | Bits, primes and modulo |
| 5 | FINAL | Explaining your full method |

Stuck? Use the tiered hints in [HINTS.md](HINTS.md) before the walkthrough. Each hint is a little stronger than the one before.

## Practice on your own

You can run GHOST VECTOR alone to learn. No event is needed.

```bash
./setup.sh
```

- In `config/flags.env`, set `PHASE2_GATE=open` to open both phases at once.
- Change `SEED` and the flags, then run `docker compose down -v && ./setup.sh` to get a fresh puzzle you haven't seen.
- Check your answers with [the reference solver](../solutions/solve_all.py) only after you've tried.

## Extra challenges after you finish

- Write **one script** that solves all seven challenges automatically.
- Change `generator.py` to hide a flag in **another column**, then give it to a friend.
- Explain why an **AI tool alone can't finish** the final stage. (Hint: think about what is not in any file.)
- Research how real satellites send telemetry (look up "CCSDS").

## For instructors

- **Session length:** about 90 minutes for Phase 1 and Phase 2, plus 30 minutes for the final stage and a debrief.
- **Teams:** 2 or 3 people per team works best.
- **Debrief:** have each team explain one challenge to the room. Teaching it is how the skill sticks.
- **Fresh puzzle each time:** change `SEED` and the flags so last term's answers don't work.
- **Answers and judging:** see [WALKTHROUGH.md](WALKTHROUGH.md) and the staff package.
