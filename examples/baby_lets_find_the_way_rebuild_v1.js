// BABY LET'S FIND THE WAY — STRUDEL REBUILD v1
// Locked source: full bass + full vocal stems
// Rebuilt in Strudel: drums, percussion, keys, pads, atmosphere
// Source tempo analysis: 139.6748 BPM
// First stable beat in source: ~0.418 s after file start

samples('github:Izhevsky/TREBLO')
setcpm(139.6748 / 4)

const SONG_CYCLES = 152
const GRID_OFFSET = 0.243 // ~0.418 s at this tempo

// ---------------------------------------------------------------------------
// LOCKED SOURCE STEMS — start at cycle 0 and play once through the song
// ---------------------------------------------------------------------------
const sourceBass = s('blftw_bass')
  .slow(SONG_CYCLES)
  .gain(0.92)

const sourceVocal = s('blftw_vocal')
  .slow(SONG_CYCLES)
  .gain(0.96)

// Optional A/B references. They are deliberately NOT in the final stack.
const sourceDrumReference = s('blftw_drum_ref')
  .slow(SONG_CYCLES)
  .gain(0.75)

const sourceSynthReference = s('blftw_synth_ref')
  .slow(SONG_CYCLES)
  .gain(0.70)

// ---------------------------------------------------------------------------
// DRUM PALETTE — warm / dusty, no generated bass
// ---------------------------------------------------------------------------
const kickSparse = s('lh_kick_uzu:0 ~ lh_kick_uzu:1 ~')
  .gain('0.66 0.58')
  .lpf(3000)
  .hpf(32)

const kickFour = s('<lh_kick_uzu:0 lh_kick_uzu:1 lh_kick_uzu:2 lh_kick_uzu:0>*4')
  .gain('0.66 0.60 0.64 0.58')
  .lpf(3200)
  .hpf(32)

const clap = s('~ lh_clap_uzu:0 ~ lh_clap_uzu:1')
  .gain(0.27)
  .hpf(420)
  .lpf(6200)
  .late(0.006)
  .room(0.07)

const snareGhost = s('~ ~ lh_snare_uzu:0 ~ ~ ~ lh_snare_uzu:1 ~')
  .gain(0.08)
  .hpf(280)
  .lpf(4300)
  .late(0.010)

const hats8 = s('lh_chh_uzu:0 lh_chh_uzu:1 lh_chh_uzu:0 lh_chh_uzu:2 lh_chh_uzu:0 lh_chh_uzu:1 lh_chh_uzu:0 lh_chh_uzu:2')
  .gain('0.08 0.13 0.07 0.15 0.08 0.12 0.07 0.16')
  .hpf(3500)
  .lpf(9200)
  .late('0 0.012 0 0.016 0 0.012 0 0.018')

const openHat = s('~ lh_ohh_uzu:0 ~ lh_ohh_uzu:1')
  .gain(0.095)
  .hpf(3000)
  .lpf(8500)
  .late(0.008)

const rim = s('<~ lh_tr808_rim ~ ~ ~ ~ lh_tr808_rim ~>')
  .gain(0.07)
  .hpf(900)
  .lpf(4800)
  .room(0.12)
  .pan(0.38)

const shaker = s('lh_tr808_hat_closed*8')
  .gain('0.025 0.05 0.03 0.06 0.025 0.05 0.035 0.07')
  .hpf(5200)
  .late('0 0.014 0.004 0.016 0 0.013 0.005 0.018')
  .pan(0.62)

const drumIntro = stack(kickSparse, clap, rim)
const drumA = stack(kickSparse, clap, hats8, rim)
const drumB = stack(kickFour, clap, snareGhost, hats8, openHat, shaker, rim)
const drumBreak = stack(clap, hats8.gain(0.06), rim)
const drumAir = stack(kickSparse, clap, hats8.gain(0.075), openHat)
const drumOutro = stack(kickSparse.gain(0.48), clap.gain(0.19), rim)

const drums = arrange(
  [8, drumIntro],
  [24, drumA],
  [24, drumB],
  [16, drumBreak],
  [24, drumA],
  [16, drumAir],
  [24, drumB],
  [16, drumOutro]
).late(GRID_OFFSET)

// ---------------------------------------------------------------------------
// HARMONY — deliberately third-light / suspended voicings.
// Bass analysis is strongly centred on C, with recurring F / Ab / Eb motion.
// The source bass remains the harmonic authority.
// ---------------------------------------------------------------------------
const pad = note('<[c4,g4,bb4] [ab3,eb4,g4] [f3,c4,eb4] [g3,d4,f4]>')
  .s('gm_pad_warm')
  .slow(2)
  .gain(0.055)
  .attack(0.55)
  .release(2.2)
  .hpf(190)
  .lpf(3300)
  .room(0.38)
  .roomsize(1.7)

const halo = note('<g5 eb5 c5 bb4>')
  .s('gm_pad_halo')
  .slow(4)
  .gain(0.022)
  .attack(0.8)
  .release(3.5)
  .hpf(700)
  .lpf(5200)
  .room(0.52)
  .pan(0.58)

const keys = note('<c4 ~ eb4 ~ g4 ~ ab4 ~>')
  .s('lh_fm_epiano')
  .gain(0.105)
  .hpf(220)
  .lpf(3900)
  .release(0.45)
  .room(0.16)
  .late(0.015)

const keysAlt = note('<~ c4 [eb4 g4] ~ ~ ab4 ~ f4 ~>')
  .s('lh_fm_epiano')
  .gain(0.085)
  .hpf(240)
  .lpf(3600)
  .release(0.38)
  .room(0.20)
  .late(0.018)

const ghostLead = note('<~ g5 ~ eb5 ~ c5 [~ bb4] ~>')
  .s('triangle')
  .slow(2)
  .gain(0.032)
  .attack(0.06)
  .release(1.5)
  .hpf(450)
  .lpf(3200)
  .room(0.50)
  .delay(0.18)
  .pan('<0.38 0.62>')

const harmonicBed = arrange(
  [8, halo.gain(0.015)],
  [24, stack(keys, pad.gain(0.038))],
  [24, stack(keysAlt, pad, halo)],
  [16, stack(pad.gain(0.030), halo.gain(0.018))],
  [24, stack(keys, pad.gain(0.045))],
  [16, stack(keysAlt.gain(0.065), ghostLead)],
  [24, stack(keys, pad, halo, ghostLead.gain(0.025))],
  [16, stack(pad.gain(0.028), halo.gain(0.014))]
).late(GRID_OFFSET)

// ---------------------------------------------------------------------------
// SMALL OLD-SCHOOL TRANSITION COLOUR — source-safe, no extra bass
// ---------------------------------------------------------------------------
const transitionStab = s('<~ lh_wavestab_vcv:0 ~ ~ ~ lh_wavestab_vcv:1 ~ ~>')
  .gain(0.055)
  .hpf(300)
  .lpf(2300)
  .room(0.22)
  .late(GRID_OFFSET + 0.01)

const texture = arrange(
  [32, silence],
  [24, transitionStab],
  [16, silence],
  [24, transitionStab.gain(0.04)],
  [16, silence],
  [24, transitionStab],
  [16, silence]
)

// ---------------------------------------------------------------------------
// FINAL MIX
// ---------------------------------------------------------------------------
stack(
  sourceBass,
  sourceVocal,
  drums,
  harmonicBed,
  texture
)
.gain(0.88)

// A/B reference options (use instead of the final stack when needed):
// stack(sourceBass, sourceVocal, sourceDrumReference, sourceSynthReference).gain(0.85)
// stack(sourceBass, sourceVocal, sourceDrumReference, harmonicBed).gain(0.86)
