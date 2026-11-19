# Player Briefing: GHOST VECTOR

Experimental relay satellite **GHOST-01** was declared lost eleven years ago. It just woke up and started broadcasting on a dead downlink. The AstroSec Deep Space Recovery Team needs you to work out what it's saying and bring it home.

## How to play

1. Log in to the **CTFd** scoreboard your organizers give you.
2. **Phase 1, Ghost Signal (G1 to G3):** download `ghost_telemetry.csv` from any Phase 1 challenge. Three flags are hidden in it.
3. **Solve G1** to unlock Phase 2.
4. **Phase 2, Silent Vector (V1 to V4):** download `vector_telemetry.csv` and `starmap.png`. Recover four navigation marker codes. They look like `NAV_WORD_WORD_N`.
5. **FINAL:** once all four markers are solved, FINAL appears. Open **HANDSHAKE.SYS** on the recovery terminal (the link is in the challenge) and lock in your markers.
6. **Judge:** explain how you solved each marker. If you pass, you get an alignment slate.
7. **Transmit:** use the slate to build the master coordinate. The terminal gives you the FINAL flag. Submit it to CTFd.

## Flag format

- Phase 1 and FINAL: `AstroSec{...}`
- Phase 2: the bare code (`NAV_...`) or wrapped (`AstroSec{NAV_...}`). Both work.
- Flags are not case sensitive.

## Hints

Each challenge has 3 hints in CTFd. The first is free, the second costs 10% of the challenge's points and the third costs 25%.

## Rules

- Don't attack the terminal, the server or other players. Everything you need is in the downloaded files.
- Any tools are allowed. The final stage needs a judge and a physical card.
