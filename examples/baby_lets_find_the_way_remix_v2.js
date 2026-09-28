// BABY LET'S FIND THE WAY — REMIX v2
// Concept: keep ONLY the original full bass + vocal stems.
// Everything else is Strudel-native, except our preserved GOLD signature kick.
// Tempo follows the source so the long-form stems stay aligned.
//
// Main feel:
// warm fast house / oldies-soul remix
// straight GOLD kick, swung hats, restrained 707/Linn backbeat,
// dusty e-piano, warm pads, native synth hook.
//
// Source timing:
// BPM ≈ 139.6748
// first stable beat ≈ 0.418 s => GRID_OFFSET ≈ 0.243 cycle
// song length ≈ 152 cycles

samples('github:Izhevsky/TREBLO')
samples('github:2lofi/Samps4Strudel')
samples('github:vasilymilovidov/samples')

setcpm(139.6748 / 4)

const SONG = 152
const GRID_OFFSET = 0.243

// ============================================================================
// 1. LOCKED SOURCE DNA
// ============================================================================

const bassStem = s('blftw_bass')
  .slow(SONG)
  .gain(0.86)

const vocalStem = s('blftw_vocal')
  .slow(SONG)
  .gain(0.98)

// ============================================================================
// 2. GOLD SIGNATURE KICK
// Preserve the approved kick identity:
// kd:12 = attack/body
// kik:9 = low tail
// The sub tail is slightly reduced here because the original bass stem is full.
// ============================================================================

const goldKick = stack(
  s('kd').n(12)
    .gain(0.92),
  s('kik').n(9)
    .clip(2.4)
    .release(0.05)
    .lpf(150)
    .gain(0.40)
)
.struct('t ~ ~ ~ t ~ ~ ~ t ~ ~ ~ t ~ ~ ~')

// Sparse versions keep the same identity.
const goldKickHalf = stack(
  s('kd').n(12).gain(0.88),
  s('kik').n(9).clip(2.4).release(0.05).lpf(150).gain(0.34)
)
.struct('t ~ ~ ~ ~ ~ ~ ~ t ~ ~ ~ ~ ~ ~ ~')

const goldKickDrop = stack(
  s('kd').n(12).gain(0.86),
  s('kik').n(9).clip(2.4).release(0.05).lpf(150).gain(0.30)
)
.struct('t ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ t ~ ~ ~')

// ============================================================================
// 3. STRUDEL-NATIVE DRUMS
// No TREBLO drum stems, no repository drum samples.
// ============================================================================

const clap = stack(
  s('RolandTR707_cp').n(0).speed(0.97).gain(0.72),
  s('LinnDrum_cp').n(0).clip(6).gain(0.30).late(0.010),
  s('RolandTR707_sd').n(1).clip(3).lpf(2400).gain(0.14).speed(0.95)
)
.struct('~ ~ ~ ~ t ~ ~ ~ ~ ~ ~ ~ t ~ ~ ~')

const hatsMain = s('LinnDrum_hh').n(1)
  .struct('t ~ t t ~ t ~ t t ~ t t ~ t ~ t')
  .gain('0.12 0.07 0.16 0.09 0.08 0.14 0.10 0.08')
  .hpf(3800)
  .lpf(9800)
  .late(0.010)

const hatsDense = s('RolandTR707_hh').n(0)
  .struct('t t t t t t t t t t t t t t t t')
  .gain('0.038 0.020 0.052 0.024 0.040 0.022 0.060 0.026')
  .hpf(4300)
  .lpf(9000)
  .late(0.015)

const ghostHat = s('RolandTR808_hh').n(0)
  .struct('~ ~ t ~ ~ t ~ ~ ~ ~ t ~ ~ ~ t ~')
  .gain(0.036)
  .hpf(4800)
  .lpf(8200)
  .late(0.018)

const openHat = s('RolandTR909_oh').n(1)
  .struct('~ ~ ~ ~ ~ ~ t ~ ~ ~ ~ ~ ~ ~ t ~')
  .gain(0.085)
  .hpf(3600)
  .lpf(9000)
  .late(0.012)

const shaker = s('RolandTR727_sh').n(1)
  .struct('t ~ t t ~ t t ~ t ~ t t ~ t t ~')
  .gain('0.030 0.050 0.034 0.060 0.032 0.054 0.038 0.066')
  .hpf(4800)
  .lpf(10500)
  .late(0.014)
  .pan(0.60)

const rim = s('RolandTR707_rim').n(0)
  .struct('~ ~ ~ t ~ ~ t ~ ~ ~ ~ t ~ t ~ ~')
  .gain(0.065)
  .hpf(900)
  .lpf(5200)
  .room(0.08)
  .late(0.008)
  .pan(0.38)

const conga = s('LinnDrum_perc').n(3)
  .struct('~ ~ t ~ ~ ~ ~ t ~ t ~ ~ ~ ~ t ~')
  .gain(0.050)
  .hpf(260)
  .lpf(4800)
  .late(0.020)
  .pan(0.67)

const tomFill = stack(
  s('OberheimDMX_mt').n(0).gain(0.10),
  s('OberheimDMX_lt').n(0).gain(0.12).late(0.08)
)
.struct('~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ t ~ t t')
.hpf(90)
.lpf(4200)

const crash = s('RolandTR909_cr').n(2)
  .struct('t ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~')
  .gain(0.11)
  .hpf(420)
  .lpf(9500)

// Drum scenes.
const beatIntro = stack(
  goldKickHalf,
  hatsMain.gain(0.07),
  rim.gain(0.045)
)

const beatA = stack(
  goldKick,
  clap,
  hatsMain,
  ghostHat,
  rim
)

const beatB = stack(
  goldKick,
  clap,
  hatsMain,
  hatsDense,
  ghostHat,
  openHat,
  shaker,
  rim,
  conga
)

const beatBreak = stack(
  goldKickDrop,
  clap.gain(0.46),
  hatsMain.gain(0.075),
  shaker.gain(0.028)
)

const beatPeak = stack(
  goldKick,
  clap,
  hatsMain,
  hatsDense,
  ghostHat,
  openHat,
  shaker,
  rim,
  conga,
  tomFill,
  crash
)

const beatOutro = stack(
  goldKickHalf.gain(0.76),
  clap.gain(0.45),
  hatsMain.gain(0.065),
  rim.gain(0.040)
)

// Source vocal activity suggests these broad sections:
// 0–28 intro/instrumental
// 28–64 vocal A
// 64–88 instrumental
// 88–108 vocal B
// 108–120 break
// 120–136 final vocal
// 136–152 outro
const drums = arrange(
  [8,  beatIntro],
  [12, beatA],
  [8,  beatB],
  [36, beatB],
  [24, beatPeak],
  [20, beatB],
  [12, beatBreak],
  [16, beatPeak],
  [16, beatOutro]
).late(GRID_OFFSET)

// ============================================================================
// 4. STRUDEL-NATIVE SYNTHS / KEYS
// Bass analysis: recurring Ab / C / F / Eb family.
// Keep chords deliberately suspended / third-light so the original bass
// remains the harmonic authority.
// ============================================================================

const rhodesA = note('<[ab3,eb4,bb4] ~ [c4,g4,bb4] ~ [f3,c4,eb4] ~ [eb3,bb3,f4] ~>')
  .s('gm_epiano2')
  .gain(0.105)
  .hpf(190)
  .lpf(4100)
  .release(0.42)
  .room(0.12)
  .late(0.014)

const rhodesB = note('<~ [ab3,eb4,bb4] ~ [c4,g4,eb4] [f3,c4,eb4] ~ ~ [eb3,bb3,f4]>')
  .s('gm_epiano2')
  .gain(0.090)
  .hpf(210)
  .lpf(3900)
  .release(0.34)
  .room(0.15)
  .late(0.018)

const pad = stack(
  note('<[ab3,eb4,bb4] [c4,g4,bb4] [f3,c4,eb4] [eb3,bb3,f4]>')
    .s('gm_pad_warm')
    .gain(0.060),
  note('<[ab4,eb5] [c5,g5] [f4,c5] [eb4,bb4]>')
    .s('gm_pad_halo')
    .gain(0.022)
)
.slow(2)
.attack(0.55)
.release(2.4)
.hpf(180)
.lpf(4200)
.room(0.34)
.roomsize(1.6)

const arp = note('<ab4 eb5 c5 eb5 f4 c5 eb5 c5>')
  .s('triangle')
  .gain(0.040)
  .attack(0.010)
  .release(0.18)
  .hpf(360)
  .lpf(3600)
  .room(0.18)
  .pan('<0.34 0.66>')

const synthHook = stack(
  note('<~ eb5 ~ c5 ~ ab4 bb4 ~>')
    .s('sawtooth')
    .gain(0.037),
  note('<~ eb5 ~ c5 ~ ab4 bb4 ~>')
    .add(note(12))
    .s('triangle')
    .gain(0.014)
)
.attack(0.025)
.release(0.30)
.hpf(300)
.lpf(3000)
.room(0.26)
.delay(0.12)
.pan('<0.43 0.57>')

const air = note('<eb6 ~ ~ c6 ~ ab5 ~ bb5>')
  .s('sine')
  .slow(2)
  .gain(0.014)
  .attack(0.18)
  .release(1.6)
  .hpf(900)
  .room(0.58)
  .pan('<0.30 0.70>')

// Intro filter colour: native noise only.
const tapeAir = s('pink')
  .gain(0.0045)
  .hpf(850)
  .lpf(6200)

// Keep the vocal sections relatively sparse.
// Let the synth hook take over during instrumental sections.
const synths = arrange(
  [8,  stack(pad.gain(0.030), tapeAir)],
  [12, stack(rhodesA.gain(0.070), pad.gain(0.040))],
  [8,  stack(rhodesB, pad.gain(0.050), arp.gain(0.025))],
  [36, stack(rhodesA, pad.gain(0.043), air)],
  [24, stack(rhodesB, pad.gain(0.060), arp, synthHook)],
  [20, stack(rhodesA, pad.gain(0.040), air.gain(0.012))],
  [12, stack(pad.gain(0.035), air.gain(0.018))],
  [16, stack(rhodesB, pad.gain(0.052), synthHook.gain(0.032), air)],
  [16, stack(pad.gain(0.025), rhodesA.gain(0.050), tapeAir)]
).late(GRID_OFFSET)

// ============================================================================
// 5. FINAL REMIX
// No original drum stem.
// No original synth/other stem.
// No generated bass.
// ============================================================================

stack(
  bassStem,
  vocalStem,
  drums,
  synths
)
.gain(0.86)

// Useful A/B:
// stack(bassStem, vocalStem, drums).gain(0.88)
// stack(bassStem, vocalStem, synths).gain(0.90)
