# Sample Sources / Provenance

Every audio file added to this repository should have a provenance entry here.

## Required fields

- Filename
- Source / creator
- Date created or acquired
- Generation tool or recording method
- Original source URL when applicable
- License / permission basis
- Processing performed after acquisition/generation
- Prompt ID for Treblo-generated material
- Notes

## House Essentials v1 — acquired 2026-09-16

### Uzu drumkit family

Files:
- `drums/kick/warm/uzu_bd_switchangel_10.wav`
- `drums/kick/warm/uzu_bd_mot4i_11.wav`
- `drums/kick/warm/uzu_bd_mot4i_12.wav`
- `drums/kick/warm/uzu_bd_switchangel_14.wav`
- `drums/clap/uzu_cp_switchangel_10.wav`
- `drums/clap/uzu_cp_mot4i_11.wav`
- `drums/hats/closed/uzu_hh_switchangel_10.wav`
- `drums/hats/closed/uzu_hh_mot4i_11.wav`
- `drums/hats/closed/uzu_hh_mot4i_14.wav`
- `drums/hats/open/uzu_oh_switchangel_10.wav`
- `drums/hats/open/uzu_oh_switchangel_11.wav`
- `drums/hats/open/uzu_oh_switchangel_12.wav`
- `drums/snare/uzu_sd_switchangel_10.wav`
- `drums/snare/uzu_sd_switchangel_11.wav`
- `drums/snare/uzu_sd_14.wav`

- Source: `tidalcycles/uzu-drumkit`
- Creators / contributors: Switch Angel, Mot4i; repository contributor notes identify Mot4i's analog-processed samples and Switch Angel's synthesized drums processed with an LA76-style analog compressor
- Original source commit: `2f3e05c70ab4d73ad053a1467adec89bd27377a0`
- Downloaded: 2026-09-16
- License: Unlicense / public-domain dedication
- Attribution required: no
- Processing: renamed only; audio unchanged
- Notes: curated for compact lo-fi/deep-house kick, clap, hat and snare duties.

### FreePats FM Synthesized Piano #1

Files:
- `synths/fm_epiano/freepats_dx7/fm_epiano_c3_v80.wav`
- `synths/fm_epiano/freepats_dx7/fm_epiano_c4_v60.wav`
- `synths/fm_epiano/freepats_dx7/fm_epiano_c4_v80.wav`
- `synths/fm_epiano/freepats_dx7/fm_epiano_c4_v100.wav`
- `synths/fm_epiano/freepats_dx7/fm_epiano_c5_v80.wav`
- `synths/fm_epiano/freepats_dx7/fm_epiano_fs2_v80.wav`
- `synths/fm_epiano/freepats_dx7/fm_epiano_fs3_v80.wav`
- `synths/fm_epiano/freepats_dx7/fm_epiano_fs4_v80.wav`

- Source: `freepats/fm-piano1`
- Creator: Roberto / FreePats
- Recording method: recorded from the Hexter software synthesizer; designed to imitate the Yamaha DX7 `E. Piano 1` sound
- Original source commit: `89a92d10b47aea841597408f5cf2e9c8164ecb00`
- Downloaded: 2026-09-16
- License: CC0 1.0 Universal
- Attribution required: no
- Processing: source FLAC converted to 44.1 kHz 16-bit PCM WAV with ffmpeg; no normalization, compression, EQ or creative processing
- Notes: intended for richer 1980s/lo-fi electric-piano layers and chord punctuation. Pitch/root is encoded in each filename.

### Karoryfer Black & Green Guitars — Green staccato

Files:
- `guitars/muted/green_staccato_a3_rr1.wav`
- `guitars/muted/green_staccato_a3_rr2.wav`
- `guitars/muted/green_staccato_a3_rr3.wav`
- `guitars/muted/green_staccato_a3_rr4.wav`
- `guitars/muted/green_staccato_a4_rr1.wav`
- `guitars/muted/green_staccato_a4_rr2.wav`
- `guitars/muted/green_staccato_a4_rr3.wav`
- `guitars/muted/green_staccato_a4_rr4.wav`

- Source: `sfzinstruments/karoryfer.black-and-green-guitars`
- Original recording: green Gretsch Anniversary guitar
- Recorded by: Brian Wood
- Original source commit: `b3b3249d37dc977a1a297bd2dc053e6d9b6b805c`
- Downloaded: 2026-09-16
- License: CC0 1.0 Universal (repository LICENSE)
- Attribution required: no under CC0
- Processing: selected A3/A4 staccato round robins renamed only; audio unchanged
- Notes: dry real-instrument material for muted disco/funk chops; preserve round-robin variation instead of repeating one hit.

SHA-256 hashes for all imported binaries are stored in `imports/house_essentials_v1/SHA256SUMS.txt`; the import workflow pins source commits for reproducibility.

## CC0 analog expansion — acquired 2026-09-16

### Michael Fischer / Technopolis TR-808

Files:
- `drums/kick/tr808_fischer/bd_50_decay_75.wav`
- `drums/kick/tr808_fischer/bd_25_decay_50.wav`
- `drums/snare/tr808_fischer/sd_50_decay_75.wav`
- `drums/snare/tr808_fischer/sd_25_decay_50.wav`
- `drums/clap/tr808_fischer/cp.wav`
- `drums/hats/tr808_fischer/ch.wav`
- `drums/hats/tr808_fischer/oh_25.wav`
- `drums/hats/tr808_fischer/oh_50.wav`
- `drums/hats/tr808_fischer/oh_75.wav`
- `drums/percussion/tr808_fischer/rs.wav`
- `drums/percussion/tr808_fischer/cb.wav`

- Source: `tidalcycles/sounds-tr808-fischer`
- Creator/copyright metadata: Michael Fischer / Technopolis
- Original source commit: `85fbecf1bec32553395625ea659e2a56dfd7c0e1`
- Downloaded: 2026-09-16
- License: CC0 1.0 Universal
- Attribution required: no
- Processing: renamed only; original WAV bytes preserved
- Verified metadata: `_soundmeta/bd8.json`, `sd8.json`, `cp8.json`, `ch8.json`, `oh8.json`, `rs8.json`, `cb8.json`

### Zach Lannes — VCV Rack wavetable stabs

Files:
- `stabs/wavestab_vcv/wavestab_0.wav`
- `stabs/wavestab_vcv/wavestab_1.wav`
- `stabs/wavestab_vcv/wavestab_2.wav`

- Source: `lannzach/sounds-wavestab`
- Creator: Zach Lannes
- Original source commit: `d3cfdf1d11afd5984be13a5f027cd970a6b21373`
- Provenance: created in VCV Rack
- Downloaded: 2026-09-16
- License: CC0 1.0 Universal
- Attribution required: no
- Processing: renamed only; original WAV bytes preserved
- Verified metadata: `wavestab.cleanmeta`

### Bernard Gray — fretless bass

Files:
- `bass/fretless_c/flbass_finger_short_neck.wav`
- `bass/fretless_c/flbass_finger_short_bridge.wav`
- `bass/fretless_c/flbass_pick_short.wav`
- `bass/fretless_c/flbass_palm_mute.wav`
- `bass/fretless_c/flbass_ghost.wav`

- Source: `cleary/samples-flbass`
- Creator: Bernard Gray
- Instrument/chain: Maton JB4 fretless bass; Aguilar TH500 DI; Focusrite Scarlett 8i8
- Original source commit: `f0c5f4ee19c2825060a5d5bfda9508f601e81b20`
- Downloaded: 2026-09-16
- License: CC0 1.0 Universal
- Attribution required: no
- Source processing: recorded dry and normalized to -1 dB by the creator
- TREBLO processing: renamed only; original WAV bytes preserved
- Verified metadata: `flbass.cleanmeta`, `README.md`, `LICENSE`

### Excluded after review

`tidalcycles/sounds-Dirty` was reviewed but not imported: its relevant TR-909 metadata declares `CC-BY-SA-NC`, which conflicts with this repository's commercial-use-safe source policy.

## Template — Treblo generation

### `filename.wav`

- Source: Treblo
- Created by: repository owner
- Generated: YYYY-MM-DD
- Type: AI-generated output
- Prompt ID: TRB-XXX-001
- Processing: none / describe edits
- License / permission basis: document applicable rights/terms at time of generation
- Notes:

## Template — original recording

### `filename.wav`

- Source: Original user-created recording
- Recorded: YYYY-MM-DD
- Recording method/device:
- Processing:
- License / permission basis: user-owned recording
- Notes:

## Template — external CC sample

### `filename.wav`

- Source:
- Creator:
- Original URL:
- Downloaded: YYYY-MM-DD
- License:
- Attribution required: yes/no
- Processing:
- Notes:

## Policy

Do not add audio of unclear provenance. A free download is not automatically redistributable. Do not upload ripped commercial recordings unless all required rights for redistribution and use have been cleared.
