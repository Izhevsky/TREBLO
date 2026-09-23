# TREBLO MIDI→Strudel Converter — Compact RC1 audit

Date: 2026-09-24
Fixture: ROBOTER.mid (+ reference audio for AUDIO ALIGNED comparison)
Status: STATIC_CODE_AUDIT; COMPACT output not yet browser-runtime-verified in this audit.

## What works

- Compact output is structurally separated into named musical roles and phrase blocks.
- Source timing remains floating-point / non-quantized.
- `setcps(1)` keeps the representation in seconds.
- A reusable helper representation is used:
  - `tone(MIDI pitch, velocity, legato)`
  - `drum(velocity, legato)`
- Drums are split into clap / closed hat / kick / snare roles.
- Arrangement is expressed as references to phrase constants, making manual rearrangement possible.
- Exact duplicate phrase reuse is already visible for some roles (for example silent clap sections).

## Size / compactness

For this fixture:
- AUDIO ALIGNED text: ~29,957 characters / 41 lines
- COMPACT text: ~24,046 characters / 633 lines
- Character reduction: only about 19.7%

So RC1 is substantially more readable structurally, but only modestly smaller as text.

## Main issues to address

### 1. Phrase mining is too strict

Near-repeated drum/bass phrases remain separate because small microtiming/gate differences prevent exact reuse.

Next step:
- build tolerance-aware phrase fingerprints;
- distinguish note identity / rhythmic skeleton / velocity / gate / microtiming;
- allow phrase reuse with a compact correction layer.

### 2. Instrument mapping is still generic

- Electric bass track is rendered with `.s('sawtooth')`.
- Distorted-electric-guitar track is rendered with `.s('triangle')`.

This preserves notes but not the MIDI instrument identity. Native/GM mode should use a verified MIDI-program→Strudel-sound mapping table, with safe fallback only when no verified mapping exists.

### 3. Drum note-off / gate semantics need special handling

MIDI drum note lengths are often implementation artifacts rather than musical durations. RC1 currently exports very small legato values for drum hits. In COMPACT musical mode, one-shot drum semantics should be preferred or at least configurable, while raw note-off timing stays preserved in canonical data / EXACT mode.

### 4. Long cross-boundary gates are technically preserved but hard to edit

Some melodic notes have very large legato values because gates cross phrase boundaries. This is correct to preserve, but Compact could expose those as explicit ties/holds or separate continuation metadata to make editing easier.

## Timing comparison checkpoint

COMPACT arrangement totals approximately 51.0491 s.
AUDIO ALIGNED export totals approximately 53.9414 s.

This difference is not automatically a bug because COMPACT is source-MIDI timing while AUDIO ALIGNED may include audio-reference offset/corrections. Compare against EXACT:
- if EXACT is also ~51.0491 s, source-timing preservation is behaving consistently;
- if EXACT differs, investigate Compact segmentation / time normalization.

## RC1 verdict

Compact RC1 proves the architecture:
source events → role split → phrase blocks → editable arrangement.

But it is not yet “human compact” enough. The next important branch should focus on:
1. tolerance-aware phrase deduplication;
2. verified instrument mapping;
3. one-shot drum gate policy;
4. stronger readability reduction without quantizing source timing.

