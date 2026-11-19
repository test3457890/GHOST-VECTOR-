# Changelog

## 1.1.0 (2026-11-18)

- Added the Learning Guide: concepts, tools, practice exercises, learning path and instructor notes.
- Added the full Walkthrough with tested code for every challenge.
- Added the reference solver in `solutions/`.
- README now has a docs table and practice-mode instructions.

## 1.0.0 (2026-11-13)

- Merged Ghost Satellite and Project Silent Vector into one app, GHOST VECTOR.
- Ghost Satellite's three tiers are now all active at once as G1, G2 and G3 (previously one tier at a time).
- Silent Vector's four tiers are kept as V1 to V4, with the judge and slate final stage.
- Phase 2 unlocks once any Phase 1 flag is submitted (set `PHASE2_GATE=open` to skip the gate).
- All flags now come from `config/flags.env`. No real flag is in the source code.
- Marker codes and the master coordinate are checked against SHA256 hashes only.
- One port (8080), one container, one setup script.
