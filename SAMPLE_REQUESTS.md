# Sample Production Queue

Requests discovered while producing Strudel tracks are recorded here before generating or sourcing new audio.

## Request format

### REQ-NNN — Name

- Priority: HIGH / MEDIUM / LOW
- Status: TODO / GENERATING / REVIEW / DONE
- Category:
- Description:
- Character:
- One-shot / Loop:
- Mono / Stereo:
- Duration:
- Pitch / key:
- BPM / bars (loops only):
- Dry / wet preference:
- Variations required:
- Preferred source: Treblo / original recording / CC0 search / other verified source
- Suggested Treblo Prompt ID:
- Destination folder:
- Target Strudel bank:

## Initial production batch

### REQ-001 — Dusty house kicks

- Priority: HIGH
- Status: TODO
- Category: Drums / kick
- Character: warm, rounded, dusty late-80s house; short decay; restrained sub; subtle cassette wear
- One-shot / Loop: One-shot
- Mono / Stereo: Mono preferred
- Variations required: 8
- Preferred source: Treblo
- Suggested Treblo Prompt ID: TRB-KICK-001
- Destination folder: `drums/kick/dusty/`
- Target Strudel bank: `lh_kick_dusty`

### REQ-002 — Dry dusty claps

- Priority: HIGH
- Status: TODO
- Category: Drums / clap
- Character: old drum-machine clap, dry, dark, slightly inconsistent, cassette-softened highs
- One-shot / Loop: One-shot
- Mono / Stereo: Mono or narrow stereo
- Variations required: 8
- Preferred source: Treblo
- Destination folder: `drums/clap/dusty/`
- Target Strudel bank: `lh_clap_dusty`

### REQ-003 — Closed hats

- Priority: HIGH
- Status: TODO
- Category: Drums / hats
- Character: dark metallic closed hats, old drum-machine feel, multiple subtle timbral variations
- One-shot / Loop: One-shot
- Variations required: 10
- Preferred source: Treblo
- Destination folder: `drums/hats/closed/`
- Target Strudel bank: `lh_chh`

### REQ-004 — Open hats

- Priority: HIGH
- Status: TODO
- Category: Drums / hats
- Character: restrained old-school open hats, not bright or modern
- One-shot / Loop: One-shot
- Variations required: 6
- Preferred source: Treblo
- Destination folder: `drums/hats/open/`
- Target Strudel bank: `lh_ohh`

### REQ-005 — Rhodes / electric-piano chords

- Priority: HIGH
- Status: TODO
- Category: Chords
- Description: minor7, major7, dominant7 and minor9 voicings
- Character: warm, worn, soulful, slightly unstable, mostly dry
- One-shot / Loop: One-shot
- Variations required: 12–20 total
- Preferred source: Treblo or original instrument recording
- Destination folder: `chords/rhodes/`
- Target Strudel banks: chord-specific `lh_rhodes_*`

### REQ-006 — Analog house stabs

- Priority: HIGH
- Status: TODO
- Category: Stabs
- Character: dark vintage polysynth/organ/e-piano house stabs, short decay, subtle detune
- One-shot / Loop: One-shot
- Variations required: 8–12
- Preferred source: Treblo
- Suggested Treblo Prompt ID: TRB-STAB-001
- Destination folder: `stabs/analog/`
- Target Strudel bank: `lh_stab_analog`

### REQ-007 — Muted disco guitar

- Priority: HIGH
- Status: TODO
- Category: Guitar
- Character: dry muted disco/funk chord chops and dead-note articulations
- One-shot / Loop: One-shot preferred
- Variations required: 12–20
- Preferred source: Treblo or original recording
- Suggested Treblo Prompt ID: TRB-GTR-001
- Destination folders: `guitars/disco/`, `guitars/muted/`, `guitars/scratches/`
- Target Strudel banks: `lh_guitar_disco`, `lh_guitar_muted`, `lh_guitar_scratch`

### REQ-008 — Organic percussion

- Priority: MEDIUM
- Status: TODO
- Category: Percussion
- Character: shaker, tambourine, conga/bongo, rim, wood/metal hits; dusty and human
- One-shot / Loop: One-shot
- Variations required: 4–8 per useful family
- Preferred source: Treblo / original recordings / verified CC0
- Destination folder: appropriate `drums/` subfolder

### REQ-009 — Cassette beds

- Priority: MEDIUM
- Status: TODO
- Category: Texture / tape
- Character: steady hiss, motor/transport character, subtle hum, non-distracting
- One-shot / Loop: Long texture
- Mono / Stereo: either
- Duration: 20–60 seconds
- Variations required: 3–5
- Preferred source: original recording / Treblo / verified CC0
- Destination folders: `textures/tape/hiss/`, `textures/tape/transport/`, `textures/tape/hum/`
- Target Strudel banks: `lh_tape_hiss`, `lh_tape_transport`, `lh_tape_hum`

### REQ-010 — Vinyl pops and beds

- Priority: MEDIUM
- Status: TODO
- Category: Texture / vinyl
- Character: subtle continuous groove noise plus separate isolated pops/clicks
- One-shot / Loop: both
- Variations required: 3–5 beds + 10–20 isolated events
- Preferred source: original recording / verified CC0
- Destination folders: `textures/vinyl/beds/`, `textures/vinyl/pops/`, `textures/vinyl/clicks/`
- Target Strudel banks: `lh_vinyl`, `lh_vinyl_pop`, `lh_vinyl_click`
