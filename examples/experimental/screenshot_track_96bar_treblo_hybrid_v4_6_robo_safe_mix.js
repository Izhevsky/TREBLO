// ═══════════════════════════════════════════════════════════════════════════
// SCREENSHOT TRACK — 96 BAR TREBLO HYBRID v4.6 ROBO SAFE MIX
// 122 BPM · A minor
//
// v4.6:
// - local ROBO pack integrated as user bank "robo"
// - removed violin-like intro triangle pad
// - more headroom to stop crackle/clipping
// - peak sections use fewer simultaneous layers
// - ROBO samples are used as accents/section events, not piled onto every beat
//
// Local ROBO bank after Import Sounds Folder:
// robo:0 = ROBOTER semi-bass phrase
// robo:1 = ROBO KICK
// robo:2 = ROBO SNARE
// robo:3 = ROBO KICK + SNARE
// ═══════════════════════════════════════════════════════════════════════════

samples({
  tkick:    'drums/kick/warm/uzu_bd_switchangel_10.wav',
  tkick808: 'drums/kick/tr808_fischer/bd_50_decay_75.wav',
  tclap:    'drums/clap/uzu_cp_switchangel_10.wav',
  tchh:     'drums/hats/closed/uzu_hh_switchangel_10.wav',
  tohh:     'drums/hats/open/uzu_oh_switchangel_10.wav',
  trim:     'drums/percussion/tr808_fischer/rs.wav',
  tcow:     'drums/percussion/tr808_fischer/cb.wav',

  tgtr1: 'guitars/muted/green_staccato_a3_rr1.wav',
  tgtr2: 'guitars/muted/green_staccato_a3_rr2.wav',
  tgtr3: 'guitars/muted/green_staccato_a4_rr1.wav',
  tgtr4: 'guitars/muted/green_staccato_a4_rr2.wav',

  epc4:  'synths/fm_epiano/freepats_dx7/fm_epiano_c4_v80.wav',
  fbc:   'bass/fretless_c/flbass_finger_short_neck.wav',
  vstab: 'stabs/wavestab_vcv/wavestab_0.wav'
}, 'https://raw.githubusercontent.com/Izhevsky/TREBLO/main/')

setcpm(122 / 4)

// HEADROOM FIRST.
// Raise only after confirming the crackle is gone.
const MASTER = 0.55

// ───────────────────────────────────────────────────────────────────────────
// DRUMS
// ───────────────────────────────────────────────────────────────────────────

const KICK = stack(
  s("tkick*4")
    .speed("1 .998 1.003 .997")
    .gain(.56)
    .lpf(4200)
    .hpf(28),

  s("tkick808*4")
    .gain(.055)
    .lpf(650)
    .hpf(24)
)

const KICK_PEAK = stack(
  s("tkick*4")
    .speed("1 .998 1.003 .997")
    .gain(.58)
    .lpf(4800)
    .hpf(28),

  s("tkick808*4")
    .gain(.060)
    .lpf(700)
    .hpf(24)
)

const KICK_SOFT = stack(
  s("tkick ~ tkick ~")
    .gain(.33)
    .lpf(1800)
    .hpf(30),

  s("tkick808 ~ tkick808 ~")
    .gain(.030)
    .lpf(460)
)

const KICK_BRIDGE =
  s("tkick ~ ~ ~ tkick ~ ~ ~")
    .gain(.36)
    .lpf(2300)
    .hpf(30)

const CLAP = stack(
  s("~ tclap ~ tclap")
    .gain(.19)
    .hpf(700)
    .lpf(7600),

  s("~ sd ~ sd")
    .bank("AkaiLinn")
    .gain(.030)
    .hpf(550)
    .lpf(9200)
)

const CLAP_PEAK = stack(
  s("~ tclap ~ tclap")
    .gain(.205)
    .hpf(700)
    .lpf(8200),

  s("~ sd ~ sd")
    .bank("AkaiLinn")
    .gain(.034)
    .hpf(550)
    .lpf(9800)
)

const CLAP_LIGHT =
  s("~ tclap ~ tclap")
    .gain(.11)
    .hpf(900)
    .lpf(6200)

const HATS = stack(
  s("tchh*16")
    .gain(".035 .065 .045 .090 .040 .062 .048 .085 .035 .068 .045 .095 .040 .060 .050 .082")
    .hpf(4400)
    .lpf(12000)
    .swingBy(.18, 8),

  s("hh*8")
    .bank("AkaiLinn")
    .gain(".009 .016 .011 .020 .009 .015 .011 .018")
    .hpf(6600)
    .lpf(14000)
    .swingBy(.18, 4)
)

const HATS_DARK =
  s("tchh*8")
    .gain(".035 .050 .038 .060 .035 .048 .040 .058")
    .hpf(4400)
    .lpf(7800)
    .swingBy(.18, 4)

const HAT_ACCENT =
  s("hh:1")
    .bank("RolandTR707")
    .struct("~ ~ t ~ ~ ~ t ~ ~ ~ t ~ ~ ~ t ~")
    .gain(.052)
    .hpf(4700)
    .lpf(10800)

const HAT_ALT =
  s("hh:1")
    .bank("RolandTR707")
    .struct("~ t ~ ~ ~ t ~ t ~ ~ t ~ ~ t ~ ~")
    .gain(.050)
    .hpf(4800)
    .lpf(11000)

const OPENHAT =
  s("[~ tohh]*4")
    .gain(.040)
    .hpf(3800)
    .lpf(11800)

const OPENHAT_PEAK =
  s("[~ tohh]*4")
    .gain(.045)
    .hpf(3900)
    .lpf(12500)

const TOM =
  s("tkick")
    .struct("~ ~ ~ t ~ ~ t ~ ~ ~ ~ t ~ ~ t ~")
    .hpf(250)
    .lpf(560)
    .gain(.18)

const TOM_ALT =
  s("tkick808")
    .struct("~ ~ t ~ ~ ~ ~ t ~ t ~ ~ ~ ~ t ~")
    .hpf(220)
    .lpf(650)
    .gain(.13)

const PERC_A = stack(
  s("trim")
    .struct("~ ~ t ~ ~ ~ t ~ ~ t ~ ~ ~ ~ t ~")
    .gain(.040)
    .hpf(1000)
    .lpf(5400),

  s("tcow")
    .struct("~ ~ ~ t ~ ~ ~ ~ ~ ~ ~ t ~ ~ ~ ~")
    .gain(.007)
    .hpf(900)
    .lpf(3900)
)

const PERC_B = stack(
  s("trim")
    .struct("~ t ~ ~ ~ ~ t ~ ~ t ~ ~ ~ t ~ ~")
    .gain(.040)
    .hpf(1050)
    .lpf(5900),

  s("tcow")
    .struct("~ ~ t ~ ~ ~ ~ ~ ~ t ~ ~ ~ ~ ~ ~")
    .gain(.008)
    .hpf(900)
    .lpf(4100)
)

const RIDE =
  s("rd*8")
    .bank("RolandTR909")
    .gain(.016)
    .hpf(5800)
    .lpf(13800)
    .swingBy(.18, 4)

const CRASH =
  s("cr")
    .bank("RolandTR909")
    .gain(.040)
    .hpf(2000)
    .lpf(14000)
    .slow(8)

// ───────────────────────────────────────────────────────────────────────────
// LOCAL ROBO PACK
// ───────────────────────────────────────────────────────────────────────────

// 4.033 sec phrase ≈ 2 bars at ~120 BPM.
// 1.025 tightens it toward 122 BPM.
// Used with NO normal synth bass underneath in B1.
const ROBOTER =
  s("<robo:0 ~ ~ ~>")
    .speed(1.025)
    .gain(.14)
    .hpf(65)
    .lpf(1900)

// Alternate kick — used only in one 2-bar peak cell.
const ROBO_KICK =
  s("robo:1*4")
    .gain(.42)
    .hpf(30)
    .lpf(2200)

// Snare has a lot of low body, so high-pass it.
const ROBO_SNARE =
  s("~ robo:2 ~ robo:2")
    .gain(.10)
    .hpf(180)
    .lpf(7200)

// Composite transition hit.
// In a 4-bar section this places the event late in the section.
const ROBO_FILL =
  s("~ ~ ~ robo:3")
    .slow(4)
    .gain(.075)
    .hpf(80)
    .lpf(6500)

// ───────────────────────────────────────────────────────────────────────────
// BASS
// ───────────────────────────────────────────────────────────────────────────

const bassNotesA =
  "<[a1 ~ a1 ~ e2 ~ g1 ~] [a1 ~ c2 ~ e2 ~ g1 ~] [f1 ~ f1 ~ c2 ~ e2 ~] [g1 ~ d2 ~ g1 ~ e2 ~]>"

const bassNotesB =
  "<[a1 ~ e2 a1 ~ g1 e2 ~] [a1 ~ c2 e2 ~ g1 e2 ~] [f1 ~ c2 f1 ~ e2 c2 ~] [g1 ~ d2 g1 ~ e2 d2 ~]>"

const bassNotesPeak =
  "<[a1 e2 a1 ~ g1 e2 a1 ~] [a1 c2 e2 ~ g1 e2 c2 ~] [f1 c2 f1 ~ e2 c2 f1 ~] [g1 d2 g1 ~ e2 d2 g1 ~]>"

const BASS_A = stack(
  note(bassNotesA)
    .s("sawtooth")
    .attack(.004)
    .decay(.14)
    .sustain(.065)
    .release(.05)
    .lpf(720)
    .lpq(1.05)
    .hpf(40)
    .gain(.165),

  note(bassNotesA)
    .s("sine")
    .lpf(180)
    .gain(.040)
)

const BASS_B = stack(
  note(bassNotesB)
    .s("sawtooth")
    .attack(.004)
    .decay(.13)
    .sustain(.055)
    .release(.045)
    .lpf(810)
    .lpq(1.10)
    .hpf(40)
    .gain(.172),

  note(bassNotesB)
    .s("sine")
    .lpf(185)
    .gain(.041)
)

const BASS_PEAK = stack(
  note(bassNotesPeak)
    .s("sawtooth")
    .attack(.003)
    .decay(.11)
    .sustain(.045)
    .release(.04)
    .lpf(900)
    .lpq(1.15)
    .hpf(42)
    .gain(.178),

  note(bassNotesPeak)
    .s("sine")
    .lpf(190)
    .gain(.043)
)

const BASS_BRIDGE =
  note("<a1 ~ ~ e2 f1 ~ ~ c2 c2 ~ ~ g1 g1 ~ e2 ~>")
    .s("sawtooth")
    .attack(.008)
    .decay(.18)
    .sustain(.055)
    .release(.08)
    .lpf(520)
    .hpf(42)
    .gain(.130)

// ───────────────────────────────────────────────────────────────────────────
// HARMONY
// ───────────────────────────────────────────────────────────────────────────

const chordNotesA =
  "<[a3,c4,e4,g4] [f3,a3,c4,e4] [c4,e4,g4,b4] [g3,b3,d4,e4]>"

const chordNotesB =
  "<[c4,e4,g4,a4] [a3,c4,e4,f4] [e4,g4,b4,c5] [b3,d4,e4,g4]>"

const chordNotesHigh =
  "<[e4,g4,a4,c5] [c4,e4,f4,a4] [g4,b4,c5,e5] [d4,e4,g4,b4]>"

const CHORDS_A = stack(
  note(chordNotesA)
    .s("piano")
    .clip(.42)
    .hpf(200)
    .lpf(8200)
    .room(.08)
    .gain(.038),

  note(chordNotesA)
    .s("triangle")
    .attack(.008)
    .decay(.27)
    .sustain(.035)
    .release(.18)
    .hpf(200)
    .lpf(3600)
    .gain(.017)
)

const CHORDS_B = stack(
  note(chordNotesB)
    .s("piano")
    .clip(.38)
    .hpf(210)
    .lpf(8600)
    .room(.09)
    .gain(.039),

  note(chordNotesB)
    .s("triangle")
    .attack(.008)
    .decay(.25)
    .sustain(.035)
    .release(.18)
    .hpf(200)
    .lpf(3900)
    .gain(.017)
)

const CHORDS_HIGH =
  note(chordNotesHigh)
    .s("piano")
    .clip(.26)
    .hpf(400)
    .lpf(10000)
    .room(.10)
    .gain(.020)

const CHORDS_BRIDGE =
  note(chordNotesA)
    .s("piano")
    .clip(.62)
    .hpf(210)
    .lpf(4900)
    .room(.15)
    .gain(.028)

const STAB_A =
  note("<[~ [a4,c5,e5] ~ ~] [~ [f4,a4,c5] ~ ~] [~ [c5,e5,g5] ~ ~] [~ [g4,b4,d5] ~ ~]>")
    .s("piano")
    .clip(.13)
    .hpf(560)
    .lpf(9000)
    .gain(.020)

const STAB_B =
  note("<[~ ~ [a4,c5,e5] ~] [~ [f4,a4,c5] ~ ~] [[c5,e5,g5] ~ ~ ~] [~ ~ [g4,b4,e5] ~]>")
    .s("piano")
    .clip(.11)
    .hpf(600)
    .lpf(9400)
    .gain(.021)

// ───────────────────────────────────────────────────────────────────────────
// GUITAR / COLOUR
// ───────────────────────────────────────────────────────────────────────────

const GUITAR_A =
  s("<tgtr1 tgtr2 tgtr1 tgtr2>")
    .struct("~ t ~ ~ ~ ~ t ~")
    .hpf(300)
    .lpf(7200)
    .room(.05)
    .gain(.034)

const GUITAR_B =
  s("<tgtr2 tgtr3 tgtr1 tgtr4>")
    .struct("~ ~ t ~ ~ t ~ ~")
    .hpf(320)
    .lpf(7600)
    .room(.05)
    .gain(.036)

const GUITAR_PEAK = stack(
  GUITAR_A,

  s("<tgtr3 tgtr4 tgtr3 tgtr4>")
    .struct("~ ~ ~ t ~ ~ t ~")
    .hpf(420)
    .lpf(9000)
    .gain(.014)
)

const EP_TINE_A =
  s("<epc4 epc4 epc4 ~>")
    .struct("~ t ~ ~ ~ ~ t ~")
    .gain(.021)
    .hpf(760)
    .lpf(8800)
    .room(.05)

const EP_TINE_B =
  s("<epc4 ~ epc4 ~>")
    .struct("~ ~ t ~ ~ t ~ ~")
    .gain(.022)
    .hpf(800)
    .lpf(9000)
    .room(.05)

const FRETLESS_GHOST =
  s("<~ ~ fbc ~>")
    .struct("~ ~ t ~ ~ ~ ~ t")
    .gain(.028)
    .hpf(60)
    .lpf(1500)

const VCV_ACCENT =
  s("<~ ~ ~ vstab>")
    .struct("~ ~ ~ ~ ~ ~ t ~")
    .gain(.050)
    .hpf(1100)
    .lpf(6200)
    .room(.05)

// ───────────────────────────────────────────────────────────────────────────
// HOOKS
// ───────────────────────────────────────────────────────────────────────────

const LEAD_A =
  note("<[~ ~ e5 ~] [~ c5 ~ e5] [g5 ~ e5 ~] [~ d5 ~ b4]>")
    .s("triangle")
    .attack(.010)
    .decay(.15)
    .sustain(.025)
    .release(.09)
    .hpf(380)
    .lpf(5000)
    .room(.08)
    .delay(.040)
    .delaytime(.369)
    .delayfeedback(.14)
    .gain(.018)

const LEAD_B =
  note("<[~ a4 c5 ~] [e5 ~ ~ c5] [~ g4 c5 e5] [d5 ~ b4 ~]>")
    .s("sawtooth")
    .attack(.008)
    .decay(.13)
    .sustain(.018)
    .release(.07)
    .hpf(400)
    .lpf(4400)
    .room(.07)
    .delay(.040)
    .delaytime(.369)
    .delayfeedback(.14)
    .gain(.014)

const BRIDGE_LEAD =
  note("<[a4 ~ ~ e5] [~ c5 ~ ~] [g4 ~ b4 ~] [~ d5 ~ e5]>")
    .s("sine")
    .attack(.08)
    .decay(.30)
    .sustain(.07)
    .release(.24)
    .hpf(350)
    .lpf(3400)
    .room(.12)
    .gain(.014)

const LEAD_PEAK = stack(
  LEAD_A,

  note("<[~ ~ a5 ~] [~ g5 ~ e5] [c6 ~ g5 ~] [e5 ~ d5 ~]>")
    .s("sine")
    .attack(.016)
    .decay(.18)
    .sustain(.02)
    .release(.12)
    .hpf(700)
    .lpf(6000)
    .room(.09)
    .gain(.009)
)

// Clean sine-only pad.
// The old triangle pad that sounded like a violin is gone.
const PAD =
  note("<[a4,e5] [f4,c5] [c5,g5] [g4,d5]>")
    .s("sine")
    .attack(.50)
    .decay(.45)
    .sustain(.20)
    .release(.60)
    .hpf(400)
    .lpf(2800)
    .room(.12)
    .gain(.008)

// ───────────────────────────────────────────────────────────────────────────
// ARRANGEMENT
// ───────────────────────────────────────────────────────────────────────────

// INTRO 0–16
const I1 =
  CHORDS_BRIDGE

const I2 = stack(
  KICK_SOFT,
  HATS_DARK,
  CHORDS_BRIDGE
)

const I3 = stack(
  KICK_SOFT,
  HATS_DARK,
  BASS_A,
  CHORDS_A
)

const I4 = stack(
  KICK,
  CLAP_LIGHT,
  HATS,
  BASS_A,
  CHORDS_A
)

// DEVELOPMENT 16–40
const D1 = stack(
  KICK,
  CLAP,
  HATS,
  PERC_A,
  BASS_A,
  CHORDS_A
)

const D2 = stack(
  KICK,
  CLAP,
  HATS,
  OPENHAT,
  BASS_A,
  CHORDS_A,
  GUITAR_A
)

const D3 = stack(
  KICK,
  CLAP,
  HATS,
  HAT_ALT,
  TOM,
  BASS_B,
  CHORDS_A,
  STAB_A,
  GUITAR_A
)

const D4A = stack(
  KICK,
  CLAP,
  HATS,
  OPENHAT,
  BASS_B,
  CHORDS_B,
  GUITAR_B,
  LEAD_A
)

const D4B = stack(
  KICK,
  ROBO_SNARE,
  HATS,
  OPENHAT,
  BASS_B,
  CHORDS_B,
  GUITAR_B,
  LEAD_A
)

const D5 = stack(
  KICK_SOFT,
  CLAP_LIGHT,
  HATS_DARK,
  BASS_B,
  CHORDS_B,
  GUITAR_A,
  LEAD_A
)

const D6 = stack(
  KICK_PEAK,
  CLAP,
  HATS,
  OPENHAT_PEAK,
  PERC_B,
  BASS_B,
  CHORDS_B,
  GUITAR_B,
  VCV_ACCENT,
  ROBO_FILL
)

// CLIMAX 40–64
const C1 = stack(
  KICK_PEAK,
  CLAP_PEAK,
  HATS,
  OPENHAT_PEAK,
  TOM,
  BASS_PEAK,
  CHORDS_B,
  STAB_A,
  GUITAR_A,
  LEAD_A
)

const C2 = stack(
  KICK_PEAK,
  CLAP_PEAK,
  HATS,
  RIDE,
  PERC_B,
  BASS_PEAK,
  CHORDS_B,
  CHORDS_HIGH,
  GUITAR_B,
  LEAD_B
)

const C3 = stack(
  KICK_SOFT,
  HATS_DARK,
  BASS_B,
  CHORDS_BRIDGE,
  GUITAR_A,
  BRIDGE_LEAD,
  PAD
)

// 60–62: normal final peak
const C4A = stack(
  KICK_PEAK,
  CLAP_PEAK,
  HATS,
  OPENHAT_PEAK,
  RIDE,
  BASS_PEAK,
  CHORDS_B,
  GUITAR_PEAK,
  LEAD_PEAK
)

// 62–64: ROBO takeover.
// Main Uzu kick/clap are removed here, so the new samples don't overload them.
const C4B = stack(
  ROBO_KICK,
  ROBO_SNARE,
  HATS,
  RIDE,
  BASS_B,
  CHORDS_B,
  GUITAR_PEAK,
  LEAD_PEAK,
  CRASH,
  VCV_ACCENT
)

// BRIDGE 64–80

// ROBOTER gets its own low-frequency space.
// No BASS_BRIDGE in these four bars.
const B1 = stack(
  KICK_BRIDGE,
  HATS_DARK,
  ROBOTER,
  CHORDS_BRIDGE,
  BRIDGE_LEAD
)

const B2 = stack(
  KICK_BRIDGE,
  HATS_DARK,
  BASS_BRIDGE,
  CHORDS_BRIDGE,
  GUITAR_A,
  FRETLESS_GHOST,
  BRIDGE_LEAD
)

const B3 = stack(
  KICK,
  CLAP_LIGHT,
  HATS_DARK,
  BASS_A,
  CHORDS_A,
  STAB_A,
  GUITAR_A,
  EP_TINE_A
)

const B4A = stack(
  KICK_PEAK,
  CLAP,
  HATS,
  OPENHAT,
  BASS_B,
  CHORDS_B,
  GUITAR_B,
  LEAD_B
)

const B4B = stack(
  KICK_PEAK,
  ROBO_SNARE,
  HATS,
  OPENHAT,
  BASS_B,
  CHORDS_B,
  GUITAR_B,
  LEAD_B,
  VCV_ACCENT
)

// OUTRO 80–96
const O1A = stack(
  KICK,
  CLAP,
  HATS,
  OPENHAT,
  BASS_A,
  CHORDS_A,
  GUITAR_A,
  LEAD_A
)

const O1B = stack(
  KICK,
  CLAP,
  HATS,
  BASS_A,
  CHORDS_A,
  STAB_A,
  GUITAR_A,
  EP_TINE_A
)

const O2 = stack(
  KICK,
  CLAP,
  HATS,
  BASS_A,
  CHORDS_A,
  GUITAR_A
)

const O3 = stack(
  KICK_SOFT,
  CLAP_LIGHT,
  HATS_DARK,
  BASS_BRIDGE,
  CHORDS_BRIDGE,
  GUITAR_A
)

const O4 = stack(
  KICK_BRIDGE,
  HATS_DARK,
  CHORDS_BRIDGE
)

arrange(
  // INTRO
  [4, I1],
  [4, I2],
  [4, I3],
  [4, I4],

  // DEVELOPMENT
  [4, D1],
  [4, D2],
  [4, D3],
  [2, D4A],
  [2, D4B],
  [4, D5],
  [4, D6],

  // CLIMAX
  [8, C1],
  [8, C2],
  [4, C3],
  [2, C4A],
  [2, C4B],

  // BRIDGE
  [4, B1],
  [4, B2],
  [4, B3],
  [2, B4A],
  [2, B4B],

  // OUTRO
  [2, O1A],
  [2, O1B],
  [4, O2],
  [4, O3],
  [4, O4]
)
.gain(MASTER)