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

