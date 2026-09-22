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
