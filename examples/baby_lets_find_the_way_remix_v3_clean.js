// BABY LET'S FIND THE WAY — REMIX v3 CLEAN BASE
// Goal: remove the "mud" and first lock the groove.
// Original: bass + vocal only.
// Everything else: Strudel-native, plus our GOLD signature kick.
//
// IMPORTANT:
// v2 used an estimated GRID_OFFSET of 0.243 cycle (~418 ms).
// Analysis of the separated drum stem shows the bar grid is much closer
// to the file start, so v3 removes that offset completely.
//
// Start with this minimal version. Do not add pads/chords until the groove
// feels right against the source bass and vocal.

samples('github:Izhevsky/TREBLO')
samples('github:2lofi/Samps4Strudel')
samples('github:vasilymilovidov/samples')

setcpm(139.6748 / 4)

const SONG = 152

// ---------------------------------------------------------------------------
// SOURCE DNA
// ---------------------------------------------------------------------------

const bassStem = s('blftw_bass')
  .slow(SONG)
  .gain(0.90)

const vocalStem = s('blftw_vocal')
  .slow(SONG)
  .gain(0.98)

// ---------------------------------------------------------------------------
// GOLD KICK
// Same identity, but less sub tail because the full source bass is present.
// ---------------------------------------------------------------------------

const kick = stack(
  s('kd').n(12)
    .gain(0.88),

  s('kik').n(9)
    .clip(2.4)
    .release(0.05)
    .lpf(145)
    .gain(0.26)
)
.struct('t ~ ~ ~ t ~ ~ ~ t ~ ~ ~ t ~ ~ ~')

// ---------------------------------------------------------------------------
// SIMPLE BACKBEAT
// ---------------------------------------------------------------------------

const clap = stack(
  s('RolandTR707_cp').n(0)
    .speed(0.97)
    .gain(0.52),

  s('RolandTR707_sd').n(1)
    .speed(0.95)
    .lpf(2500)
    .gain(0.10)
)
.struct('~ t ~ t')

// ---------------------------------------------------------------------------
// ONE HAT FAMILY ONLY
// Offbeat hat first. No dense 16th layer, no congas, no toms.
// ---------------------------------------------------------------------------

const hat = s('LinnDrum_hh').n(1)
  .struct('~ t ~ t ~ t ~ t')
  .gain('0.075 0.11 0.08 0.12')
  .hpf(4200)
  .lpf(9000)
  .late(0.008)

const ghostHat = s('RolandTR808_hh').n(0)
  .struct('~ ~ ~ t ~ ~ ~ ~')
  .gain(0.028)
  .hpf(5000)
  .lpf(8200)
  .late(0.014)

// ---------------------------------------------------------------------------
// VERY SPARSE SYNTH MOTIF
// Single notes only: no guessed chords/pads yet.
// F / Ab / C / Eb are used as a conservative colour set.
// ---------------------------------------------------------------------------

const synthHook = note('<f5 ~ ~ ab5 ~ ~ c5 ~ eb5 ~ ~ ~>')
  .slow(2)
  .s('triangle')
  .gain(0.028)
  .attack(0.015)
  .release(0.32)
  .hpf(420)
  .lpf(2800)
  .room(0.16)
  .delay(0.10)
  .pan('<0.44 0.56>')

// A tiny electric-piano echo, deliberately monophonic.
const keys = note('<~ c5 ~ ~ ~ eb5 ~ ~>')
  .slow(2)
  .s('gm_epiano2')
  .gain(0.035)
  .hpf(300)
  .lpf(3200)
  .release(0.30)
  .room(0.10)

// ---------------------------------------------------------------------------
// FINAL CLEAN BASE
// ---------------------------------------------------------------------------

stack(
  bassStem,
  vocalStem,
  kick,
  clap,
  hat,
  ghostHat,
  synthHook,
  keys
)
.gain(0.90)

// ---------------------------------------------------------------------------
// DEBUG:
// 1) First test only bass + vocal + kick:
// stack(bassStem, vocalStem, kick).gain(0.94)
//
// 2) Then add backbeat:
// stack(bassStem, vocalStem, kick, clap, hat).gain(0.92)
//
// 3) Only after that use the full stack above.
// ---------------------------------------------------------------------------
