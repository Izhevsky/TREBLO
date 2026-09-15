# Treblo Sample Generation Log

Store reproducible generation recipes here. Each accepted generation should receive a stable prompt ID.

## ID convention

`TRB-CATEGORY-NNN`

Examples:

- `TRB-KICK-001`
- `TRB-CLAP-001`
- `TRB-GTR-001`
- `TRB-STAB-001`
- `TRB-SYNTH-001`

## Prompt template

### TRB-XXX-001 — Short name

- Category:
- Status: TEST / KEEP / REJECT
- Generated: YYYY-MM-DD
- Desired variants:
- Output files:
- Rating:

**Prompt**

> Describe the sonic result rather than requesting an exact copy of a named copyrighted recording. Specify era, source/instrument, transient, body, decay, pitch if needed, noise/imperfection, stereo/mono, dry/wet state, and explicitly request an isolated sample with no background music when appropriate.

**Post-processing**

- Trim:
- Gain/normalization:
- Resample:
- Other:

**Notes**


## Starter prompt — dusty house kick

### TRB-KICK-001 — Dusty late-80s house kick

- Category: Kick
- Status: TEST
- Desired variants: 8

**Prompt**

> Single isolated late-1980s underground house kick drum, vintage analog/digital drum-machine character, warm rounded body, controlled low end, short decay, slightly worn cassette saturation, dusty softened transient, restrained sub bass, dry, mono-compatible, no reverb, no percussion, no background music, clean one-shot sample.

## Starter prompt — muted disco guitar

### TRB-GTR-001 — Dry muted disco guitar chop

- Category: Guitar
- Status: TEST
- Desired variants: 12

**Prompt**

> Single isolated dry muted disco-funk electric guitar chord chop, late-1970s to early-1980s studio character, short tight palm-muted articulation, slightly worn analog recording tone, warm midrange, no drums, no bass, no background music, no delay, no reverb, one-shot.

## Starter prompt — analog house stab

### TRB-STAB-001 — Dusty analog minor-7 stab

- Category: Chord stab
- Status: TEST
- Desired variants: 6

**Prompt**

> Single isolated vintage analog polysynth minor seventh chord stab for late-1980s underground house, short decay, warm detuned oscillators, dark low-pass filtering, subtle hardware saturation and pitch instability, mostly dry, no drums, no bass, no background music, one-shot.
