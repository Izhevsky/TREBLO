# USER ROBO PACK v1 — integration notes

Source: user-uploaded original audio, 2026-09-22.

## Files received

Planned repository-safe names:

- `roboter_semibass_120bpm.wav` — source name `01 ROBOTER.wav`; user describes it as a semi-bass synth.
- `robo_kick.wav` — source name `02 ROBO KICK.wav`.
- `robo_snare.wav` — source name `03 ROBO SNARE.wav`.
- `robo_kick_snare.wav` — source name `04 ROBO KICK + SNARE.wav`.

## Analysis snapshot

- ROBOTER: ~4.033 s, stereo 44.1 kHz; tempo estimate around 120 BPM; strongly low-frequency. Treat as a 2-bar semibass/transition phrase, not a permanent main bass.
- ROBO KICK: ~0.629 s; extremely sub-heavy. Best as quiet low reinforcement or an alternate robotic kick.
- ROBO SNARE: ~0.637 s; unusually strong low body. High-pass when layered with the main kick so it does not collapse the low end.
- ROBO KICK + SNARE: ~1.261 s; composite/phrase-like hit with multiple transients. Best as a rare fill or section-transition punch.

## Current track integration plan

For the 122 BPM A-minor 96-bar branch:

1. Keep the approved Uzu + 808 kick as the main identity.
2. Layer ROBO KICK quietly only in selected 2/4-bar peak cells.
3. Use ROBO SNARE as an occasional robotic accent/fill, not on every backbeat.
4. Use ROBO KICK + SNARE before a rebuild/final peak.
5. Use ROBOTER sparsely in bridge/rebuild transitions. Because the file is about 4.033 s long, a starting alignment candidate at 122 BPM is roughly `.speed(1.025)`; confirm by ear before promoting.
6. Never let ROBOTER run continuously underneath the existing synth bass until harmonic compatibility is checked.

## Intro fix

The unpleasant bowed/violin-like sound at the beginning was most likely the long-attack triangle layer of the PAD. v4.5 removes that triangle voice and removes the long PAD entirely from bars 0–8.

## Storage status

The exact WAV uploads and metadata are preserved in the project Library workspace:
`/TREBLO/04_SAMPLE_BANKS/USER_ROBO_PACK_v1/`

Physical WAV commit to GitHub is still pending because the current GitHub connector write path supports text/blobs only through explicit content payloads and does not accept the uploaded binary file references directly.
