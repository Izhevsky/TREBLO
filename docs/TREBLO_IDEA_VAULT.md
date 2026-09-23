# TREBLO IDEA VAULT

A curated notebook of interesting Strudel techniques, bank names, rhythmic ideas, arrangement tricks, and sound-design combinations worth reusing later.

## Status labels

- **REFERENCE** — user supplied an interesting example; not yet verified in the user's current Strudel session.
- **RUNTIME_VERIFIED** — confirmed to run in the user's current Strudel browser.
- **MUSICAL_APPROVAL** — user explicitly approved the result by ear.
- Do not copy third-party audio into TREBLO without redistribution rights.

---

## 2026-09-23 — “AliensBuiltThePyramids” / G-Conlon
Status: **REFERENCE / USER-SUPPLIED CODE / NOT YET RUNTIME-VERIFIED**

Source title supplied by user:
“AliensBuiltThePyramids(silly frozen water goons.... finnagityers)” — G-Conlon, 2026-09-22.

### Banks / sounds worth remembering

Percussion:
- `mridangam_gumki`
- `mridangam_ka`
- `mridangam_chaapu`
- `mridangam_ardha`
- `hh`
- `bd:3`

GM / melodic colour:
- `gm_acoustic_bass`
- `gm_epiano1`
- `gm_blown_bottle`
- `gm_acoustic_guitar_nylon`
- `gm_choir_aahs`

These are references from the submitted code only; qualify them separately before promoting to GOLD.

### Reusable code ideas

1. **Probability-based acoustic percussion**
   - Dense mridangam patterns with `*3?`, `*6?`, etc.
   - Random sample variation through `.n(irand(...))`.
   - Very low individual gains, then group-level gain/pan.

2. **Random melodic index → scale mapping**
   - `irand(6)` + `.rib(43,8)` + `.scale(...)`.
   - Strong candidate for generative hooks that stay inside a tonal frame.

3. **Pentatonic key contrast**
   - Alternate or layer major/minor pentatonic regions instead of writing a fixed melody.
   - Example concept from the reference: Bb major pentatonic vs C minor pentatonic.

4. **Timbre morphing via bank alternation**
   - Acoustic bass ↔ e-piano.
   - Blown bottle ↔ e-piano ↔ nylon guitar.
   - Useful for a single generative note engine feeding several instrument identities.

5. **Moving spectral/reverb envelope**
   - Patterned `.hpf("<...@2 ...>")` together with patterned `.room("<...>")`.
   - Reuse for long evolving sections without adding more notes.

6. **Sparse arrangement by destructive masking**
   - `.every(8, x => x.mask(0))`
   - `.sometimesBy(0.2, x => x.mask(0))`
   - Good for making generative layers breathe rather than continuously stack.

7. **Distortion + vibrato as identity**
   - Moderate `.distort(...)` plus `.vib(...)` on a restrained melodic layer.
   - Consider for psychedelic/outsider-house textures, not on the whole mix.

8. **Delayed minimal kick**
   - Very quiet `bd:3` with long delay can function as a ghost pulse instead of a conventional house kick.

9. **Half-time / double-time drama**
   - Same source patterns are reused with `.fast(2)`, `.fast(8)`, and patterned `.slow(...)`.
   - Strong arrangement trick: change perceived density without inventing new material.

10. **Choir as periodic reveal**
    - `gm_choir_aahs` appears only in a later section, with tremolo and periodic masking.
    - Useful for one “impossible / alien / sacred” climax colour.

11. **Long-form arrange() architecture**
    - Short 2-bar reset cells between long 16/32-bar sections.
    - The resets create chapter boundaries without a full stop.
    - Large terminal `silence` block is a simple render/export tail technique.

### What is especially relevant to TREBLO house work

- Mridangam as a non-obvious ghost-percussion layer under house drums.
- `gm_epiano1` as a potentially useful built-in fallback/reference against TREBLO FM e-piano.
- `gm_blown_bottle` as a sparse psychedelic top-line texture.
- `gm_acoustic_guitar_nylon` as an alternate organic transient/chop source.
- `gm_choir_aahs` for rare climax/bridge colour, never continuous.
- `rib + scale` for generative but harmonically bounded hooks.
- Patterned HPF + room automation as a cheap way to create movement without additional polyphony.
- Masking and probability as preferred ways to create variation instead of stacking ever more layers.

### Next qualification candidates

Test individually in the user's current Strudel browser before production use:
1. `mridangam_ka` / `mridangam_gumki`
2. `gm_epiano1`
3. `gm_blown_bottle`
4. `gm_acoustic_guitar_nylon`
5. `gm_choir_aahs`
6. `rib(...)` behavior in the current runtime
7. `.trem(...)` behavior in the current runtime
8. patterned `.room(...)` + `.hpf(...)` automation

### TREBLO adaptation idea

For a future 122 BPM deep/stoner-house track:
- keep the approved Uzu/808 kick;
- put mridangam very low in the mix as syncopated ghost percussion;
- use a single random-note engine constrained to A minor pentatonic;
- alternate FM e-piano / blown-bottle / muted guitar timbres;
- automate HPF + room over 8/16 bars;
- use choir only as a late climax event;
- create variation primarily with mask/probability and time-density changes.



## Learning principle — “наслушанность / насмотренность”

Use reference code as vocabulary training, not as a template to copy verbatim.

What to retain from strong examples:
- unusual but effective sound-bank choices;
- rhythm-generation strategies;
- scale / pitch-constraining techniques;
- phrasing density and use of silence;
- arrangement pacing;
- timbral contrast;
- modulation / FX movement;
- probability and masking strategies;
- ways of creating development from a small amount of source material.

For new TREBLO generations:
1. recombine learned techniques in new harmonic/rhythmic contexts;
2. prefer transformation and synthesis over literal reproduction;
3. preserve the musical principle, not the surface sequence;
4. promote only techniques that work musically in our own tracks;
5. keep building a broader internal vocabulary so first-pass generations become stronger over time.

This vault is therefore a **musical coding reference library / listening-and-looking memory**, not a collection of snippets to imitate one-to-one.



## Capture rule — what was interesting

Whenever a new reference is added to this vault, also record a short human-readable reflection:

- **What was discovered**
- **What especially caught attention**
- **Why it matters for future TREBLO tracks**
- **What should be tested or reused first**

This reflection is not a rating and not a claim that the reference is objectively better. It is a practical note about which techniques expand our musical/code vocabulary the most.



---

## 2026-09-23 — “Scales (again) — Riffin in D Major” / r/strudel screenshot
Status: **REFERENCE / SCREENSHOT-DERIVED / NOT YET RUNTIME-VERIFIED**

Visible account in screenshot: `u/MalsAngryGhost`.

### Clearly visible sound / code vocabulary

- `samples('github:yaxu/clean-breaks')`
- `supersaw`
- `pink`
- `white`
- `bd` with bank `mc303`
- `folkharp`
- Perlin-controlled filter and delay movement
- `irand(...)` constrained by a major scale
- `.shuffle(...)`, `.fast(...)`, `.seg(...)`, `.ply(...)`
- pattern masking
- occasional self-removal through `.sometimesBy(..., x => x.hush())`
- small motif array + `pick(...)`
- `jux(iter(4))`
- noise used rhythmically rather than as static background

### What was discovered

The strongest structural idea is **hierarchical variation**: the pitch vocabulary can stay simple while selection, masking, stereo motion, rhythmic density, filtering and delay each evolve at different speeds.

The screenshot also shows a useful distinction between:
- generating notes,
- selecting motifs,
- deciding when a layer is present,
- and independently moving its timbre/spatial behavior.

That separation is valuable because it creates evolution without requiring more simultaneous layers.

### What especially caught attention

1. **Perlin as a slow modulation source**  
   Not for melody itself, but for filter/delay movement. This is a much better fit for TREBLO than randomizing everything because the musical phrase remains recognizable while the sound keeps breathing.

2. **A motif bank plus `pick(...)`**  
   Pre-compose several strong mini-phrases, then let the code choose among them. This is a very promising middle ground between fully hand-written melody and uncontrolled random generation.

3. **Noise as an actual rhythmic voice**  
   Pink/white noise is enveloped, filtered, masked and panned like percussion. This is more musically useful than a permanent vinyl-noise bed.

4. **Silence as variation**  
   `.sometimesBy(..., x => x.hush())` and masks remove events instead of adding more. This directly supports our current goal of richer arrangements without mix overload.

5. **Different timescales inside one voice**  
   Fast notes with very slow filter/delay movement. This can make an 8- or 16-bar loop feel much longer and more alive.

### Why it matters for future TREBLO tracks

For our Deep / Lo-Fi / Stoner House direction, the best adaptation is:
- keep kick + bass comparatively stable,
- build 3–5 strong upper-register motifs,
- select/reorder them algorithmically,
- create arrangement through mask/hush rather than extra tracks,
- use slow Perlin movement on filter/delay/room,
- treat noise as occasional percussion,
- reserve wide stereo/jux behavior for upper layers only.

### What to test first

1. Perlin-controlled LPF/delay on an existing TREBLO hook.
2. A 4-motif `pick(...)` bank in A minor.
3. `.sometimesBy(..., x => x.hush())` on guitar/EP layers.
4. Rhythmic pink/white-noise percussion.
5. `jux(iter(4))` only on a high-passed melodic layer.
