# TREBLO MIDI→Strudel Converter — Compact RC1 audit

Date: 2026-09-24
Fixture: ROBOTER.mid (+ reference audio for AUDIO ALIGNED comparison)
Status: **RUNTIME_VERIFIED + HUMAN_AUDIBLE_VERIFIED for strudel_compact.js**

The user ran the generated `strudel_compact.js` in the current browser Strudel session and reported that it works and sounds very close to the reference WAV.

## Confirmed correctness on this fixture

- MIDI duration: 51.049103854 s.
- Compact total duration: 51.049103854 s.
- Compact timing approximation error reported by `compact_plan.json`: ~7.1e-15 s (floating-point noise; effectively zero).
- Source MIDI notes: 516.
- Compact plan source-event coverage: 516 / 516 unique event IDs.
- Missing source events: 0.
- Duplicate source-event assignment: 0.
- Phrase size: 4 bars.
- Generated patterns: 34.
- Arrangement references: 36.
- Reused references beyond first occurrence: 2.

This is strong evidence that the Compact branch preserves the source MIDI event set and timing on this fixture while producing a phrase-oriented arrangement.

## Instrument mapping correction

The currently uploaded Compact export uses proper verified GM-oriented mappings:
- electric bass program 33 → `gm_electric_bass_finger`
- distorted/overdriven guitar program 29 → `gm_overdriven_guitar`
- drum roles → `bd`, `sd`, `hh`, `cp`

An earlier audit note that described Compact as using `sawtooth` / `triangle` was based on an earlier pasted export and is **superseded by this current runtime-tested file**.

`track_map.json` still leaves the user-facing `mapping` field null, so a later UI/version should expose the resolved mapping explicitly instead of only embedding it in the generated code / compact plan.

## What works

- Compact output is structurally separated into named musical roles and phrase blocks.
- Source timing remains floating-point / non-quantized.
- `setcps(1)` keeps the representation in seconds.
- A reusable helper representation is used:
  - `tone(MIDI pitch, velocity, legato)`
  - `drum(velocity, legato)`
- Drums are split into clap / closed hat / kick / snare roles.
- Arrangement is expressed as references to phrase constants, making manual rearrangement possible.
- Current output runs successfully in Strudel and is judged by the user to be very close to the source WAV.

## Size / compactness

For this fixture:
- EXACT: ~30,097 characters
- COMPACT: ~24,154 characters
- character reduction: ~19.7%

So RC1 is substantially more readable structurally, but only modestly smaller as text.

## Main issues to address for RC2

### 1. Phrase mining is too strict

Only one actual phrase identity is reused: `clap_2_1` appears three times, yielding two reused references. Near-repeated drum/bass phrases remain separate because microtiming/gate differences prevent equivalence.

Next step:
- build tolerance-aware phrase fingerprints;
- separate note identity / rhythmic skeleton / velocity / gate / microtiming;
- allow phrase reuse with a compact correction layer;
- preserve canonical timing exactly outside the compressed presentation.

### 2. Expose resolved instrument mapping

The generated code and compact plan know the GM sounds, but `track_map.json` has `mapping: null`.

RC2 should expose:
- MIDI program
- detected role
- resolved Strudel sound
- fallback reason, if any
- manual override

without altering timing.

### 3. Drum note-off / gate semantics

MIDI drum note lengths can be implementation artifacts rather than musically meaningful durations. Compact currently preserves very short gate values.

Recommended RC2 option:
- Preserve MIDI gate
- One-shot musical mode
- Minimum gate

Canonical/Exact data must always retain the original note-off timing.

### 4. Long cross-boundary gates

Some notes legitimately cross phrase boundaries and therefore create large legato ratios. Compact preserves them, which is correct, but editing would improve if RC2 could represent these as explicit ties/holds or continuation metadata.

## Audio alignment observation

Report measurements:
- MIDI duration: 51.049 s
- reference audio duration: 49.534 s
- global alignment offset: +2.8380 s
- audio tempo estimate: 97.509 BPM
- MIDI tempo: 97.636 BPM
- drift: -20.4 ppm

The tempo estimates are close, but the positive ~2.838 s offset together with a shorter audio duration means AUDIO ALIGNED should be auditioned separately before treating that alignment as validated. Compact/Exact source timing is independently confirmed by the current runtime test.

## RC1 conclusion

Compact RC1 has crossed an important threshold:

**MIDI source → lossless event coverage → timing-preserving phrase representation → runnable Strudel output → close perceptual match to the reference WAV.**

The next branch should improve compression/readability rather than rewrite the timing core.
