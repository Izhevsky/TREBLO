# TREBLO Sample Catalog

This file is the human-readable inventory of samples exposed through `strudel.json`.

## Naming convention

Strudel bank names use the `lh_` prefix to avoid collisions with built-in banks.

Examples: `lh_kick_dusty`, `lh_clap_dusty`, `lh_rhodes_cm7`, `lh_tape`, `lh_vinyl_pop`.

## Drums

| Bank | Count | Character | Status |
|---|---:|---|---|
| `lh_kick_uzu` | 4 | Analog-processed / synthesized compact electronic kicks; Switch Angel + Mot4i | Ready |
| `lh_clap_uzu` | 2 | Short electronic claps with analog-processing character | Ready |
| `lh_chh_uzu` | 3 | Dark/compact closed hats, suitable for swung house patterns | Ready |
| `lh_ohh_uzu` | 3 | Short open hats for offbeat house accents | Ready |
| `lh_snare_uzu` | 3 | Electronic snares for quiet clap layering / fills | Ready |
| `lh_deep_cassette_12x_reel` | 1 reel | Existing custom cassette-style kick reel | Reel / not sliced |
| `lh_tr808_kick` | 2 | Medium/long classic analog 808 kick | Ready; CC0 |
| `lh_tr808_snare` | 2 | Medium/long classic analog 808 snare | Ready; CC0 |
| `lh_tr808_clap` | 1 | Classic 808 clap | Ready; CC0 |
| `lh_tr808_hat_closed` | 1 | Closed analog hat | Ready; CC0 |
| `lh_tr808_hat_open` | 3 | Short/medium/long open analog hats | Ready; CC0 |
| `lh_tr808_rim` | 1 | 808 rim shot | Ready; CC0 |
| `lh_tr808_cowbell` | 1 | 808 cowbell | Ready; CC0 |

## Bass

| Bank | Count | Character | Status |
|---|---:|---|---|
| `lh_fretless_c` | 5 | Dry C2 fretless bass: finger, pick, palm mute and ghost articulations | Ready; CC0 |

## Chords / Stabs

| Bank | Count | Character | Status |
|---|---:|---|---|
| `lh_wavestab_vcv` | 3 | Plucky/oscillating modular wavetable stabs made in VCV Rack | Ready; CC0 |

## Guitars

| Bank | Count | Character | Status |
|---|---:|---|---|
| `lh_guitar_green_a3` | 4 | Real Gretsch Anniversary staccato A3 round robins; dry, short, useful for muted/funk chops | Ready |
| `lh_guitar_green_a4` | 4 | Real Gretsch Anniversary staccato A4 round robins | Ready |

## Synths / Keys

| Bank | Count | Character | Status |
|---|---:|---|---|
| `lh_fm_epiano` | 5 pitched anchors | DX7-style FM electric piano mapped by note for direct `note(...).s('lh_fm_epiano')` playback | Ready |
| `lh_fm_epiano_c4_vel` | 3 | DX7-style FM electric piano C4 at velocity 60/80/100 | Ready |
| `lh_fm_epiano_keys` | 5 | DX7-style FM piano anchors: C3, F#3, C4, F#4, C5 at v80 | Ready; use documented sample index / pitch handling |

`lh_fm_epiano_keys` index order is: `0=C3`, `1=F#3`, `2=C4`, `3=F#4`, `4=C5`.

## Vocals

| Bank | Count | Character | Status |
|---|---:|---|---|
| — | 0 | — | Waiting for samples |

## Textures / FX

| Bank | Count | Character | Status |
|---|---:|---|---|
| — | 0 | — | Waiting for samples |

## Curated imports

`imports/house_essentials_v1/` contains the provenance snapshot and SHA-256 checksums for the first public-domain/permissive production import.

## Maintenance rule

Whenever a sample bank is added to `strudel.json`, update this catalog in the same change.
