# TREBLO Strudel Playbook

Reusable musical patterns, sound recipes and arrangement ideas that have worked well in TREBLO/Strudel R&D.

## Rule

**Preserve what sounds good; change one sound-design dependency at a time.**

Do not promote a bank/API to "gold" until it has passed a real browser audition. Node syntax checks are not Strudel runtime verification.

Third-party/built-in Strudel sounds may be referenced here, but their raw audio must not be copied into TREBLO unless redistribution rights are verified. TREBLO-owned/generated and CC0/public-domain/redistributable material may be stored in the repo with provenance.

---

## Gold TREBLO banks

| Bank | Best use | Notes |
|---|---|---|
| `lh_kick_uzu` | main house kick | compact, analog-processed, good for fixed-kick identity |
| `lh_tr808_kick` | low kick body | layer quietly under a brighter kick |
| `lh_clap_uzu` | house clap | short electronic clap layer |
| `lh_chh_uzu` | closed hats | dark swung house patterns |
| `lh_ohh_uzu` | offbeat open hats | use sparingly |
| `lh_snare_uzu` | clap reinforcement/fills | keep lower than clap |
| `lh_fm_epiano` | 80s/lo-fi house chords | preferred richer harmonic layer |
| `lh_fretless_c` | organic bass colour | dry CC0 articulations |
| `lh_guitar_green_a3` / `lh_guitar_green_a4` | muted disco/funk chops | rotate round robins |
| `lh_wavestab_vcv` | modular stabs | use after harmonic compatibility check |
| `lh_loop_drum_house` | sampler/MPC layer | original 4-bar loops @122 BPM |
| `lh_loop_keys_house` | sampler keys | only if harmony matches |
| `lh_loop_synth_house` | atmospheric phrase | only if harmony matches |

## GOLD Lo-Fi palette — AMBER HOURS (user-approved, 2026-09-25)

This palette is preserved because the user explicitly rated the kick, bass, snare/clap, hats and synth choices as an ideal Lo-Fi reference. Treat it as a **first-choice audition palette**, not as a mandatory template. Revalidate external dependencies when reusing it in a new Strudel session.

### Kick identity — GOLD
External sources:
- `kd:12` from `github:2lofi/Samps4Strudel` = main kick body / attack
- `kik:9` from `github:vasilymilovidov/samples` = low sub-tail

Reference construction:
```js
stack(
  s('kd').n(12).gain(1),
  s('kik').n(9).clip(2.4).release(0.05).lpf(150).gain(0.55),
)
.struct("t ~ ~ ~ t ~ ~ ~ t ~ ~ ~ t ~ ~ ~")
```

Production rule:
- keep the kick itself dry / direct;
- no master-style shape/compressor on the kick identity;
- main pulse stays straight on the grid;
- use the `kik:9` layer mainly as sub reinforcement;
- protect the sub-300 Hz region for kick + bass.

### Snare / clap stack — GOLD
- `RolandTR707_cp:0` = main clap identity
- `LinnDrum_cp:0` = quieter digital clap layer
- `RolandTR707_sd:1` = quiet snare body

Reference idea:
```js
stack(
  s('RolandTR707_cp').n(0).speed(0.97).gain(0.85),
  s('LinnDrum_cp').n(0).clip(6).gain(0.45).nudge(0.01),
  s('RolandTR707_sd').n(1).clip(3).lpf(2400).gain(0.22).speed(0.95),
)
```

Keep the 707 clap dominant; Linn and snare are reinforcement, not competing mains.

### Closed-hat family — GOLD
- `LinnDrum_hh:1` = principal swung hat character
- `RolandTR707_hh:0` = denser secondary 16th layer
- `RolandTR808_hh:0` = low-level ghost-hat articulation
- `RolandTR909_oh:1` = open-hat lift

Reference behaviour:
- swing hats, not kick;
- alternate gains instead of using one static velocity;
- secondary 16ths may use controlled `degradeBy`;
- ghost hat stays quiet;
- open hat is sparse and supportive.

### Bass — GOLD synthesis recipe
This is **not a sample bank**. The successful bass identity is a layered synth recipe:

```js
stack(
  p.s('sawtooth').gain(0.5),
  p.s('sine').add(note(-12)).gain(0.45).lpf(110),
)
.attack(0.004)
.decay(0.14)
.sustain(0.52)
.release(0.1)
.lpf(cut)
.lpq(2.6)
.lpenv(1.2)
.lpattack(0.003)
.lpdecay(0.14)
.lpsustain(0.22)
.hpf(34)
```

Principle:
- saw = audible bass identity;
- sine one octave down = restrained foundation;
- short envelope;
- filtered, mono-biased low end;
- musical syncopation matters as much as timbre.

### Keys / synth palette — GOLD reference
- `gm_epiano2` = dusty Rhodes/e-piano stab identity
- `gm_pad_warm` = main pad body
- `gm_pad_halo` = upper airy pad layer
- native `supersaw` = quiet third pad colour
- `gm_string_ensemble_1` = restrained strings
- lead = two slightly detuned native saw layers + quiet square one octave down
- arp = triangle body + quiet saw edge

#### Lead recipe
```js
stack(
  p.s('sawtooth').add(note(-0.08)).gain(0.4),
  p.s('sawtooth').add(note(0.08)).gain(0.4),
  p.s('square').add(note(-12)).gain(0.16),
)
```

#### Pad recipe
```js
stack(
  note(ch).s('gm_pad_warm').gain(0.5),
  note(ch).add(note(12)).s('gm_pad_halo').gain(0.2),
  note(ch).s('supersaw').gain(0.2),
)
```

### Supporting percussion palette
Useful secondary colours from the same reference:
- `RolandTR727_sh:1` — shaker
- `RolandTR707_rim:0` — rim
- `LinnDrum_perc:3` — muted conga/percussion
- `OberheimDMX_mt:0` / `OberheimDMX_lt:0` — tom fills
- `RolandTR909_cr:2` — crash / reverse-transition source

### TREBLO rule
For Lo-Fi / deep-house generation or reconstruction, audition this palette early when the source/style allows it. Preserve the role logic:
- straight kick;
- swung hats;
- layered but restrained clap/snare;
- saw + sine-sub bass;
- dusty GM e-piano;
- warm/halo pad stack;
- restrained saturation and space.

Do not blindly paste the whole palette into every song. The semantic/code planner should choose only the roles required by the source or Producer brief.

---


## 2026-09-26 model guidance — how TREBLO should think when writing Strudel

This section is intentionally written as **instructions for an AI model that generates or revises Strudel code**.

The goal is not "produce valid JavaScript". The goal is:

> **translate a musical intention into the simplest faithful, musical, editable, runtime-safe Strudel representation.**

### 1. Preserve approved sound identities

Once a sound has been explicitly approved by ear, treat it as a frozen identity until the user asks to replace it.

Current strongest example:

**GOLD KICK 001 — AMBER HOURS**

\`\`\`js
stack(
  s('kd').n(12).gain(1),
  s('kik').n(9).clip(2.4).release(0.05).lpf(150).gain(0.55),
)
.struct("t ~ ~ ~ t ~ ~ ~ t ~ ~ ~ t ~ ~ ~")
\`\`\`

Rules:
- do not replace \`kd:12\`;
- do not replace the \`kik:9\` sub-tail;
- do not add master-style compression/shape directly to this kick identity;
- keep the kick grid straight;
- create groove mainly with hats/percussion, not by moving the kick;
- if the mix needs change, try level/filter/ducking first before changing the kick sample.

If a user says "the kick is perfect", future versions should preserve it by default.

---

### 2. Local Cymatics Lo-Fi palette — audition source, not public asset

The user supplied the Cymatics Lofi Toolkit for **internal music generation**. Raw samples must not be republished in the public TREBLO repository.

Current local role map used in experiments:

\`\`\`js
const kits = {
  house: {
    // keep GOLD kick
    kick: ['kd', 12],
    sub:  ['kik', 9],

    // local Cymatics palette
    clap:   ['cym_clap', 0],
    clap2:  ['cym_clap', 1],
    snare:  ['cym_snare', 0],

    hat:    ['cym_ch', 0],
    hat2:   ['cym_ch', 1],
    ghost:  ['cym_ch', 2],
    oh:     ['cym_oh', 0],

    shaker: ['cym_perc', 3],
    rim:    ['cym_perc', 0],
    conga:  ['cym_perc', 4],
    tomM:   ['cym_perc', 2],
    tomL:   ['cym_perc', 1],
    crash:  ['cym_crash', 0],
  },
}
\`\`\`

Treat these mappings as **audition candidates**, not immutable truth.

The important transferable lesson is the role logic:
- main clap identity + quieter second clap + quiet snare body;
- main swung closed hat + secondary dense hat + ghost hat;
- sparse open hat;
- separate percussion colours for shaker/rim/conga/fills;
- keep the best kick identity independent from the rest of the kit.

---

### 3. Write music as independent musical dimensions

A strong Strudel part should preferably separate:

\`\`\`text
PITCH CONTENT
+
RHYTHMIC STRUCTURE
+
TRANSFORMATION
+
TIMBRE / LAYERING
+
ARTICULATION
+
EXPRESSION
+
ACTIVITY IN THE ARRANGEMENT
\`\`\`

Avoid encoding everything as one giant event list when the same musical idea can be expressed structurally.

Preferred thinking:

\`\`\`js
const bassNotes = note("<c3 e3 g3 [a2 e2]>")

const bass = bassNotes
  .struct("x ~ x ~ x ~ [x x] ~")
  .trans("[-12,-24]")
  .sound("gm_acoustic_bass,gm_synth_bass_2")
  .decay(.25)
  .release(.25)
\`\`\`

The exact syntax must always be revalidated against the current Strudel runtime before production use.

The principle is more important than the literal example:

**what is played** should be separable from **when it is played**, **how it is voiced**, and **what sound renders it**.

---

### 4. Structure and expression are different things

Do not create a new musical pattern only because:
- velocity changed slightly;
- gate changed slightly;
- the same hat is a few milliseconds late;
- the sound source changed.

Think conceptually:

\`\`\`text
STRUCTURE
+ dynamics
+ articulation
+ microtiming
+ sound mapping
\`\`\`

For reconstruction:
- preserve every real expressive difference;
- reuse structure only when equivalence is provable;
- fall back to precise events when needed.

For Producer Mode:
- expression may be intentionally generated, but only in an explicit creative branch.

---

### 5. Use timbre stacking as one musical role when appropriate

If two sounds perform the same notes and together form one instrument identity, prefer thinking of them as **one role with multiple timbral layers**, not two independent musical voices.

Examples:

\`\`\`js
note(PATTERN)
  .s("gm_acoustic_bass,gm_synth_bass_2")
\`\`\`

or:

\`\`\`js
stack(
  p.s('sawtooth').gain(0.5),
  p.s('sine').add(note(-12)).gain(0.45).lpf(110),
)
\`\`\`

Use separate musical voices only when the parts actually differ in pitch/rhythm/articulation.

---

### 6. Sampler / MPC-style generation

A loop can become a new rhythmic instrument instead of remaining a passive backing loop.

Useful conceptual chain:

\`\`\`js
s("sample")
  .slice(16, "<slice-order>")
  .fast(8)
  .clip(1)
\`\`\`

Potential creative extension:

\`\`\`js
.sometimes(ply(2))
\`\`\`

Important:
- \`slice\`/reordering can be reconstruction-safe only when it reproduces known source slicing;
- probabilistic ornaments such as \`sometimes(ply(...))\` are **Producer-only** unless the original source truly contains that behaviour;
- verify each function against the current Strudel runtime before promoting it to the Technique Registry.

This is a key production idea:

\`\`\`text
LOOP
→ SLICES
→ NEW RHYTHMIC ORDER
→ ARTICULATION
→ PRODUCER VARIATION
\`\`\`

---

### 7. Diagnostic visualisation is part of the workflow

When current Strudel supports it, use visual feedback such as punchcard/piano-roll style diagnostics during development.

Goal:
- inspect timing;
- inspect density;
- inspect downstream transformations;
- see accidental double triggers;
- understand whether a pattern became too dense.

Visual diagnostics do not replace listening.

They help locate problems before audio export.

---

### 8. Separate PART CONTENT from PART ACTIVITY

A crucial arrangement concept:

\`\`\`text
PART
├── musical content
├── expression
├── sound
└── activity over song time
\`\`\`

The fact that a bassline exists is separate from the bars in which it is active.

Internal TREBLO/Producer representation should conceptually support:

\`\`\`text
Part {
  role
  pattern
  expression
  sound
  activity
}
\`\`\`

The emitter can then choose between:
- \`.mask(...)\`;
- \`arrange(...)\`;
- section-level inclusion;
- a hybrid.

---

### 9. mask() vs arrange() — choose by musical structure

A long track can be built as one \`stack()\` with each layer controlled by \`.mask()\`.

This is legitimate when:
- a layer keeps the same musical identity for a long time;
- only its activity changes;
- masks remain readable and performant.

But do **not** blindly produce a 200-bar wall of masks if it recreates the giant-code problem.

Prefer \`arrange()\` when:
- sections have clearly different musical material;
- section reuse improves readability;
- several layers change together.

Best default for long productions is often **hybrid**:

\`\`\`js
const intro = stack(...)
const groove = stack(...)
const breakdown = stack(...)
const drop = stack(...)

$: arrange(
  [16, intro],
  [32, groove],
  [16, breakdown],
  [32, drop],
)
\`\`\`

with local \`.mask()\` only where one layer needs intermittent activity.

Planner rule:

> Choose \`mask\`, \`arrange\`, or a hybrid based on **readability + runtime cost + musical structure**, not stylistic preference.

---

### 10. Natural-language Producer Assistant loop

A human should be allowed to describe a problem perceptually:

- "the hats sound like a second snare";
- "the kick should walk away into the distance";
- "the bridge arrives too abruptly";
- "the humming should overlap into the next section";
- "the vocal syllables should become the beat before the drop";
- "the track becomes static after 32 bars".

The model should translate this into a **minimal musical delta**, not rewrite the whole song.

Preferred loop:

\`\`\`text
USER LISTENS
↓
USER DESCRIBES PROBLEM
↓
INTERPRET MUSICAL INTENT
↓
LOCALIZE AFFECTED PART / SECTION
↓
PROPOSE MINIMAL CHANGE
↓
APPLY CODE DELTA
↓
AUDIO QA
↓
RUNTIME CHECK
↓
NEW VERSION
↓
USER LISTENS AGAIN
\`\`\`

This iterative workflow is preferred over one-shot "generate the perfect track".

---

### 11. Problem → measurable hypothesis

Translate subjective feedback into testable engineering hypotheses.

Example:

**"Hats sound like a second snare."**

Possible diagnostics:
- too much 2–6 kHz energy;
- envelope too long;
- strong transient too similar to snare;
- accents line up with the backbeat;
- hat sample itself is too body-heavy.

Possible minimal actions:
- audition softer hat sample;
- shorten gate/decay;
- raise HPF;
- reduce midrange;
- change accent pattern;
- reduce backbeat coincidences.

Do not apply every fix simultaneously.

Change the minimum number of variables needed to test the hypothesis.

---

### 12. Semantic transition intents

The user may describe transitions with perceptual language.

Create intent-level concepts such as:

\`\`\`text
MOVE_AWAY
APPROACH
DISSOLVE
VACUUM
OVERLAP
BUILD
DROP_PREP
TAPE_STOP
ROLE_MORPH
\`\`\`

Example:

**"kick walks away into the distance"**

may map to a controlled combination of:
- dry gain down;
- low-pass down;
- reverb amount/size up;
- transient emphasis down;
- ambience/stereo up.

Do not hard-code one effect chain as the only meaning of "distance".

The Technique Registry may contain several verified implementations.

---

### 13. Role transformation is a production technique

A source does not need to keep the same musical role.

Examples:

\`\`\`text
VOCAL
→ chopped vocal
→ rhythmic vocal
→ percussive syllables
→ drum-like roll
→ DROP
\`\`\`

Other possible morphs:

\`\`\`text
pad → riser
kick → distant transition pulse
melody → chopped texture
chord → rhythmic stab
hum → bridge glue
\`\`\`

This is a **Producer** concept, not Reconstruction.

Keep role transformation out of faithful reconstruction unless it exists in the source.

---

### 14. Vocal / syllable engine — future Producer capability

Useful future pipeline:

\`\`\`text
VOCAL SOURCE
↓
tempo warp
↓
phrase / word / syllable segmentation
↓
slice map
↓
pitch / chord compatibility
↓
rhythmic chop plan
↓
section role
\`\`\`

Potential features:
- warp from source BPM to project BPM;
- syllable slicing;
- harmonic remapping;
- gated syllable rolls;
- overlap/hum transitions;
- vocal → percussion morph.

Never assume local copyrighted vocal samples are redistributable.

Store code/analysis separately from restricted audio.

---

### 15. Audio QA after every meaningful iteration

The model should not rely only on code inspection.

After generating or materially revising a version, analyse the audio or target-runtime output where available.

Useful QA signals:
- peak level;
- RMS / approximate loudness;
- clipping;
- DC offset;
- low-end energy;
- spectral balance;
- transient density;
- pitch/chord consistency where measurable;
- kick/bass low-frequency conflict;
- hat/snare spectral overlap;
- section energy;
- unintended silence;
- abrupt section boundaries.

Audio analysis is **evidence**, not aesthetic authority.

The user still decides what sounds good.

---

### 16. Iteration journal

For every significant Producer iteration, record:

\`\`\`text
VERSION
USER FEEDBACK
DIAGNOSIS
CHANGED PARTS
CODE DELTA
AUDIO QA RESULT
USER VERDICT
\`\`\`

Example:

\`\`\`text
v17

USER:
"hats sound like another snare"

DIAGNOSIS:
long decay + too much mid transient + backbeat accents

CHANGE:
shorter hat articulation
less 2–5 kHz
reduced accents on snare beats

QA:
peak unchanged
hat/snare spectral overlap reduced

USER:
better
\`\`\`

Successful problem/solution pairs may later become GOLD Producer knowledge.

---

### 17. GOLD knowledge is not only a sound recipe

Store two types of GOLD knowledge:

**A. SOUND / MUSICAL RECIPE**
- GOLD kick;
- GOLD hat stack;
- GOLD bass design;
- GOLD chord timbre.

**B. PROBLEM → SOLUTION**
- hats feel like snare → shorten/filter/change accent/sample;
- bridge too abrupt → overlap outgoing ambience + introduce incoming layer early;
- drop lacks impact → create contrast before drop, not just more gain;
- low end collapses → inspect kick/bass role overlap before adding processing.

The second category is essential for Producer Assistant quality.

---

### 18. Reduction pass before finalising

After building a section or full track, ask:

- Which layer has no unique role?
- Which two layers compete for the same function?
- Is there enough silence?
- Are hats/percussion over-describing the groove?
- Does the bass conflict with the kick?
- Are there too many FX at once?
- Is the hook still identifiable?
- Is the code more complex than the music?

Remove unnecessary material before adding more.

---

### 19. Prefer musical contrast over raw loudness

Energy should be created through:
- density;
- register;
- instrumentation;
- rhythm;
- harmonic tension;
- filter opening;
- silence before impact;
- role changes;
- stereo contrast.

Do not create every peak by simply increasing gain or stacking more sounds.

---

### 20. Strudel is composition/arrangement; final mix may be external

Do not force every production task into Strudel.

A practical professional workflow may be:

\`\`\`text
STRUDEL
composition
pattern design
arrangement
creative sample manipulation
        ↓
EXPORT
        ↓
DAW / SuperCollider / external mix
        ↓
final mix / master
\`\`\`

When useful, export stems or role groups:

\`\`\`text
kick
drums
bass
harmony
lead
vocal
fx
\`\`\`

Keep composition logic reproducible in Strudel even if mastering happens elsewhere.

---

### 21. Reconstruction-safe vs Producer-only techniques

Maintain a strict boundary.

#### Reconstruction-safe
Allowed automatically only when source equivalence is provable:
- pattern reuse;
- exact grid notation;
- chord grouping with matching timing;
- structure/expression factoring;
- sound mapping;
- exact activity masks;
- exact section arrangement.

#### Producer-only
Require explicit creative mode:
- \`sometimes(...)\`;
- probabilistic \`ply(...)\`;
- invented fills;
- new notes;
- reharmonisation;
- new vocal chops;
- role morphing;
- humanisation not present in source;
- new transitions.

Never leak Producer logic into Reconstruction.

---

### 22. Runtime-first technique promotion

A new Strudel trick should move through:

\`\`\`text
IDEA
↓
CURRENT API CHECK
↓
MINIMAL STANDALONE TEST
↓
REAL STRUDEL RUNTIME
↓
AUDIBLE RESULT
↓
USER APPROVAL
↓
REGISTRY / GOLD
\`\`\`

Do not promote techniques based only on remembered API names or JavaScript syntax validity.

---

### 23. Model checklist before handing code to the user

Before presenting a new version, ask:

1. Did I preserve all approved sound identities?
2. Did I change only what the user asked to change?
3. Is the kick still the approved kick if it was frozen?
4. Did I separate pitch/rhythm/timbre/articulation when that improves clarity?
5. Could a repeated structure be named and reused?
6. Should this be \`mask\`, \`arrange\`, or hybrid?
7. Did I accidentally use a Producer-only trick in Reconstruction?
8. Did I introduce an unverified bank/API?
9. Is there a safe fallback?
10. Does the code run in the current Strudel runtime?
11. Did I inspect the audio result where possible?
12. Is the code understandable to another model or human?
13. Did I add complexity that does not create audible value?
14. Can the next iteration modify one part without rewriting everything?

---

### 24. Core philosophy for models

The best Strudel code is not the code with the most tricks.

It is code where a human can understand:

\`\`\`text
WHAT is playing
WHY it is there
WHEN it is active
HOW it is articulated
WHAT sound gives it identity
HOW it changes across the arrangement
\`\`\`

The preferred workflow is:

\`\`\`text
LISTEN / ANALYSE
↓
UNDERSTAND MUSICAL ROLE
↓
CHOOSE SIMPLE STRUCTURE
↓
CHOOSE SOUND
↓
ADD EXPRESSION
↓
PLACE IN ARRANGEMENT
↓
RUN IN STRUDEL
↓
ANALYSE AUDIO
↓
LISTEN AGAIN
↓
ITERATE WITH MINIMAL DELTAS
\`\`\`

**Do not confuse code complexity with musical sophistication.**
**Do not confuse loudness with impact.**
**Do not replace an approved sound identity without a reason.**
**Do not rewrite the whole track to fix one local problem.**

---

## Built-in bank roles

These are references to Strudel built-ins; they are not TREBLO sample assets.

- `RolandTR808`: low body, subby kick/snare colour.
- `RolandTR707`: front edge, clap/rim, classic house attack.
- `RolandTR909`: bright hats, open hats, ride/crash.
- `AkaiLinn`: dry digital snare/hat transient layer.
- `RhythmAce`: vintage bright/airy percussion colour.

---

## Screenshot groove — reusable rhythmic DNA

### Four-on-floor kick
```js
sound("bd:0")
  .bank("RolandTR909")
  .struct("t ~ ~ ~ t ~ ~ ~ t ~ ~ ~ t ~ ~ ~")
```

### Low tom made from kick body
```js
sound("bd:0")
  .bank("RolandTR909")
  .struct("~ ~ ~ t ~ ~ t ~ ~ ~ ~ t ~ ~ t ~")
  .hpf(250)
  .lpf(500)
```

### Rolling 16th hat
```js
sound("hh*16")
  .bank("RolandTR909")
  .gain("0.12 0.22 0.15 0.29 0.13 0.20 0.16 0.27 0.12 0.23 0.15 0.30 0.13 0.20 0.17 0.27")
  .swingBy(0.18, 8)
```

### Secondary hat
```js
sound("hh:1")
  .bank("RolandTR707")
  .struct("~ ~ t ~ ~ ~ t ~ ~ ~ t ~ ~ ~ t ~")
```

### Hat fill
```js
sound("hh:2")
  .bank("RolandTR909")
  .struct("~ t ~ ~ ~ t t ~ ~ t ~ t ~ ~ t t")
  .slow(4)
```

---

## Premium drum layering recipes

### Kick: 707 attack + 808 body
```js
stack(
  sound("bd*4").bank("RolandTR707").gain(.68).lpf(4200).hpf(30),
  sound("bd*4").bank("RolandTR808").gain(.115).lpf(720).hpf(25)
)
```

### Clap: 707 identity + Linn digital transient
```js
stack(
  sound("~ cp ~ cp").bank("RolandTR707").gain(.27).hpf(720).lpf(7600),
  sound("~ sd ~ sd").bank("AkaiLinn").gain(.08).hpf(450).lpf(9200)
)
```

### Hats: 909 groove + quiet Linn/RhythmAce air
Keep the secondary layers quiet. The expensive impression comes from articulation, not brightness alone.

---

## Bass recipes

### Hypnotic A pattern
```js
"<[a1 ~ a1 ~ e2 ~ g1 ~] [a1 ~ c2 ~ e2 ~ g1 ~] [f1 ~ f1 ~ c2 ~ e2 ~] [g1 ~ d2 ~ g1 ~ e2 ~]>"
```

### Development B pattern
```js
"<[a1 ~ e2 a1 ~ g1 e2 ~] [a1 ~ c2 e2 ~ g1 e2 ~] [f1 ~ c2 f1 ~ e2 c2 ~] [g1 ~ d2 g1 ~ e2 d2 ~]>"
```

### Peak pattern
```js
"<[a1 e2 a1 ~ g1 e2 a1 ~] [a1 c2 e2 ~ g1 e2 c2 ~] [f1 c2 f1 ~ e2 c2 f1 ~] [g1 d2 g1 ~ e2 d2 g1 ~]>"
```

Preferred concept: filtered saw body + quiet sine foundation. Keep sub mono-ish and restrained.

---

## Harmony / hook vocabulary

### Core progression
A minor house bed:
- Am7
- Fmaj7
- Cmaj7
- G6 / G-family turnaround

### Chord voicings
```js
const chordNotesA =
  "<[a3,c4,e4,g4] [f3,a3,c4,e4] [c4,e4,g4,b4] [g3,b3,d4,e4]>"

const chordNotesB =
  "<[c4,e4,g4,a4] [a3,c4,e4,f4] [e4,g4,b4,c5] [b3,d4,e4,g4]>"
```

### Sparse lead A
```js
"<[~ ~ e5 ~] [~ c5 ~ e5] [g5 ~ e5 ~] [~ d5 ~ b4]>"
```

### Response lead B
```js
"<[~ a4 c5 ~] [e5 ~ ~ c5] [~ g4 c5 e5] [d5 ~ b4 ~]>"
```

Hooks should be sparse, repeatable and easy to remember. Prefer call/response and 8/16-bar variation over continuous melody.

---

## Harmony sound recipe

For a richer house chord without a heavy external dependency:
- triangle/sine = body,
- short piano/FM-e-piano sample = transient/tine,
- small room,
- high-pass around 150–250 Hz,
- keep the chord layer below drums/bass.

When TREBLO is available, prefer `lh_fm_epiano` over a generic piano for the late-80s/early-90s target.

---

## 96-bar arrangement blueprint

### Stable macro-form
- 0–16: intro
- 16–40: development
- 40–64: climax
- 64–80: bridge
- 80–96: outro

### Better micro-form
Use 4-bar cells inside the macro-form:
- intro: 4 + 4 + 4 + 4
- development: 4 + 4 + 4 + 4 + false pullback 4 + rebuild 4
- climax: 8 + 8 + breath 4 + final peak 4
- bridge: 4 + 4 + 4 + 4
- outro: 4 + 4 + 4 + 4

Important: the bridge should reduce density without completely killing pulse. A short "breath inside climax" before the final 4-bar peak creates more drama than one long breakdown.

---

## Runtime lessons

1. Preserve a confirmed working core before changing sound sources.
2. Add one bank or API dependency per test.
3. A JavaScript syntax pass is not browser runtime verification.
4. External `samples(...)` loading has produced parser/runtime trouble in some user sessions; keep a native/built-in fallback and smoke-test TREBLO loading separately.
5. Avoid introducing many pitched sample loops at once; baked harmony can clash with live chord progressions.
6. Keep fixed kick identity once the groove is approved; vary velocity/filter/mix before swapping the kick sample.
7. Continuous vinyl/noise is optional. The track must groove without it.


### Critical Strudel string rule: single quotes for literal URLs/paths

The main Strudel editor transpiler treats **double-quoted strings** as Mini-Notation in many contexts. Therefore a literal URL/path written like:

```js
samples({
  x: "drums/kick/warm/uzu_bd_switchangel_10.wav"
}, "https://raw.githubusercontent.com/Izhevsky/TREBLO/main/")
```

can be routed into the Mini parser and fail on the first `/` with an error such as:

`[mini] parse error ... "/" found`.

For **literal strings that must NOT be Mini-Notation**, use **single quotes**:

```js
samples({
  x: 'drums/kick/warm/uzu_bd_switchangel_10.wav'
}, 'https://raw.githubusercontent.com/Izhevsky/TREBLO/main/')

s("x*4")
```

Rule for TREBLO code generation:
- Mini patterns inside `s(...)`, `note(...)`, `struct(...)`, etc. may use double quotes.
- Literal URLs, repository shortcuts, file paths, object string values and other non-pattern strings should default to single quotes.
- If an error begins with `[mini]` and points at a slash inside a URL/path, inspect quote style before investigating CORS, WAV encoding or GitHub availability.


### Runtime-verified external sample loader — 2026-09-22

Confirmed by the user in the current browser Strudel session:

```js
samples({
  x: 'drums/kick/warm/uzu_bd_switchangel_10.wav'
}, 'https://raw.githubusercontent.com/Izhevsky/TREBLO/main/')

setcpm(122 / 4)

s("x*4").gain(.7)
```

Status:
- GitHub resource exists: VERIFIED.
- Direct `samples(map, baseURL)` loader with **single-quoted** path/base URL: RUNTIME_VERIFIED.
- `uzu_bd_switchangel_10.wav`: HUMAN_AUDIBLE_VERIFIED in Strudel.
- Previous double-quoted loader failures were quote/transpiler errors, not evidence of bad WAV data.

Do not generalize this verification to every TREBLO bank until each new source is auditioned.


### Runtime-verified TREBLO audition set — 2026-09-22

The user confirmed that the following combined audition plays correctly in the current Strudel browser session:

- `uzu_bd_switchangel_10.wav`
- `bd_50_decay_75.wav`
- `uzu_cp_switchangel_10.wav`
- `uzu_hh_switchangel_10.wav`
- `uzu_oh_switchangel_10.wav`
- `rs.wav`
- `cb.wav`
- Gretsch staccato A3/A4 round-robin files:
  - `green_staccato_a3_rr1.wav`
  - `green_staccato_a3_rr2.wav`
  - `green_staccato_a4_rr1.wav`
  - `green_staccato_a4_rr2.wav`

Status for this exact audition set:
- direct GitHub loader with single-quoted literals: RUNTIME_VERIFIED
- audio playback in the user's Strudel session: HUMAN_AUDIBLE_VERIFIED
- safe to use as the external-sample foundation of the current 96-bar screenshot reconstruction branch

This does **not** automatically verify other TREBLO banks such as FM e-piano, fretless bass, wavestabs or loops. Test those separately before production use.


### Runtime-verified melodic colour banks — 2026-09-22

The user separately confirmed successful playback of:

- FM e-piano: `synths/fm_epiano/freepats_dx7/fm_epiano_c4_v80.wav`
- fretless bass: `bass/fretless_c/flbass_finger_short_neck.wav`
- VCV wavestab: `stabs/wavestab_vcv/wavestab_0.wav`

Status:
- each resource: RUNTIME_VERIFIED in the current browser session
- each resource: HUMAN_AUDIBLE_VERIFIED
- safe to use as low-level colour layers in the current 96-bar branch
- their fixed sample pitch still matters; avoid pretending one sample is a full multisample instrument until pitch mapping/repitch behavior is explicitly qualified

v4.4 production rule:
- FM C4 is used only as a quiet tine/transient colour where C is harmonically safe.
- fretless C is used as a sparse ghost articulation only around the C-root portion of the 4-bar harmony cycle.
- VCV wavestab is high-passed and used mainly as a transition texture, so uncertain fundamental pitch does not dominate the harmony.

---

## Promotion rule

A pattern/sample/recipe becomes **GOLD** after:
1. it runs in the user's current Strudel browser,
2. the user approves it by ear,
3. source/license/provenance is known where applicable,
4. the exact code/sample reference is recorded here.



## User-recorded melody intake for Strudel

When the user records new melodic material for a current house track, request **dry WAV takes** and preserve the original performance. Preferred capture:

- 122 BPM unless the track says otherwise;
- 4/4;
- current key noted in the track spec;
- 44.1 or 48 kHz WAV, preferably 24-bit;
- no reverb, delay, limiter or master processing;
- peaks roughly between -12 and -6 dBFS;
- start exactly on bar 1 when possible;
- upload separate files for each musical role.

For the current 96-bar A-minor reconstruction branch, the most useful recording slots are:

1. **MAIN HOOK — 8 bars**: sparse, memorable, mostly A minor pentatonic / A natural minor; leave space between phrases.
2. **COUNTER HOOK — 4 bars**: higher register, answer the main hook, preferably enters off-beat.
3. **MUTED / STACCATO RIFF — 4 bars**: rhythmic, short notes; works especially well on guitar/e-piano.
4. **BRIDGE PHRASE — 8 bars**: longer notes and more air; fewer attacks than the main hook.
5. **ONE-SHOT STABS**: isolated clean notes/chords for future slicing and repitching.

After upload:
- keep the original dry take;
- make trimmed/aligned derivatives separately;
- document BPM/key/bar length/source/processing;
- add only user-owned or otherwise redistributable audio to TREBLO;
- add the resulting sample map to `strudel.json` only after browser audition.


### v4.6 ROBO safe-mix / crackle lesson — 2026-09-22

User feedback: the beat was audibly crackling/rasping.

Inspection of the four uploaded ROBO WAVs showed no sample-level clipping:
- ROBOTER peak ≈ -16.0 dBFS
- ROBO KICK peak ≈ -10.8 dBFS
- ROBO SNARE peak ≈ -4.9 dBFS
- ROBO KICK + SNARE peak ≈ -4.2 dBFS

Therefore the first production response is to treat the crackle as **mix-bus / summed-layer overload or browser audio load**, not as clipped source WAVs.

v4.6 changes:
- MASTER reduced from 0.76 to 0.55.
- Main kick / 808 body / clap / hats / bass / harmony gains reduced.
- Peak sections use fewer simultaneous layers.
- Loudness increase is created by arrangement density, not by louder kick/clap variants.
- ROBO kick/snare replace existing drum layers in the 2-bar ROBO takeover rather than stacking on top of them.
- ROBOTER gets its own low-frequency space in the first bridge cell; normal synth bass is removed there.
- Old bowed/violin-like triangle pad remains removed.

Local ROBO sample import:
- Use Strudel Sounds → Import Sounds → Import Sounds Folder.
- Folder structure should expose a `robo(4)` bank:
  - `robo:0` ROBOTER semibass
  - `robo:1` kick
  - `robo:2` snare
  - `robo:3` kick+snare composite fill

Public GitHub audio upload is intentionally withheld for this pack until redistribution rights are confirmed. The uploaded WAV metadata identifies Kraftwerk / "Die Roboter", so keep the audio private/local and store only code, analysis and integration notes in the public repository unless provenance/rights are clarified.
