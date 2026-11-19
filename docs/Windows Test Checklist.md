# Owner Windows and event VM test checklist

Use this on November 25, 2026 or later. The Windows computer hosts an isolated Linux VM; the recovery terminal is a Docker service inside that VM. Record the date, VM image, browser, CTFd version, result, and a private screenshot of failures. Do not post real flags, staff pack contents, unlock keys, event addresses, or participant records in public issues. No items below have been completed on the owner's machine.

## Setup and isolation

- [ ] Start with a fresh clone in the VM. Copy the example flag configuration to the ignored local file and replace all example values. Keep it outside screenshots and logs.
- [ ] Run `./setup.sh`. Confirm `docker compose port ghost-vector 8080` publishes `127.0.0.1:8080` by default. Verify the Windows host and another device cannot reach that loopback service.
- [ ] For an approved event network only, bind a specific private VM interface and check access from the separate player VM. Confirm the terminal is never exposed through internet port forwarding.
- [ ] Build and import the CTFd pack into a fresh private CTFd. Confirm all eight challenges, point values, unlock prerequisites, hints, and downloadable files. Restore a clean event instance after testing.

## Player interface and flows

- [ ] Open the briefing, telemetry download, navigation links, Phase 2 page, and HANDSHAKE.SYS in desktop and phone-width browsers. Check that locked sections remain locked in gated mode.
- [ ] Try an incorrect and a correct Phase 1 submission. Check the response message, unlock, refresh, browser restart, and a second independent browser session.
- [ ] Download Phase 2 files after unlock. Try an unknown file path, a disallowed download, non-JSON API calls, missing fields, oversized input, and repeated incorrect attempts. Verify controlled errors and rate limits without revealing answers.
- [ ] Submit four incorrect markers, then four correct markers in a disposable event. Confirm the judge step is required before the final coordinate. Try a wrong coordinate and a correct one; verify the scoreboard accepts the final flag.
- [ ] Test CTFd login, each challenge entry, hint display, flag submission, duplicate submission, score, and category navigation. Run the player smoke test against the exact event deployment with a disposable account, then remove it.
- [ ] Test keyboard navigation, focus visibility, 200% zoom, phone layout, readable error messages, and every visible button or form. Compare the four existing screenshots against the running app and replace stale images only with authentic, spoiler-free captures.

## Recovery and security

- [ ] Restart the terminal and verify the expected session and generated-file behavior. Test a clean backup and restore of the event configuration in private organizer storage.
- [ ] Verify container read-only mode, non-root user, capability drops, resource limits, and HTTP security headers on the deployed VM. If HTTPS is used, check `COOKIE_SECURE=1` and trusted proxy settings.
- [ ] Check that the staff pack remains encrypted and that no decrypted guides, local flags, source secrets, or private test artifacts appear in the player container or screenshots.
- [ ] Confirm the final release commit's CI passed unit, security scan, and real CTFd end-to-end jobs. Record any difference between this VM run and CI.
