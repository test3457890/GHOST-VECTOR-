#!/usr/bin/env python3
"""Staff tool: hash the master coordinate for config/flags.env.

Run this on a private machine. The coordinate itself is never stored.
"""
import getpass
import hashlib

coord = getpass.getpass("Master coordinate (hidden): ").strip().upper()
again = getpass.getpass("Repeat: ").strip().upper()
if coord != again or not coord:
    raise SystemExit("Entries did not match. Nothing written.")
print("\nPaste this line into config/flags.env:\n")
print("PRIZE_KEY_HASH=" + hashlib.sha256(coord.encode()).hexdigest())
print("\nThen restart: docker compose up -d --force-recreate")
