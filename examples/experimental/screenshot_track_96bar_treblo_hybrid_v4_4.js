// ═══════════════════════════════════════════════════════════════════════════
// SCREENSHOT TRACK — 96 BAR TREBLO HYBRID v4.4
// 122 BPM · A minor
//
// Goal:
// brighter / richer / more expensive sound without losing the approved groove.
//
// IMPORTANT:
// - avoids samples('github:...') because that form triggered the user's mini-parser
// - TREBLO files are mapped directly through one known-good base URL
// - pitched external loops are NOT used here, to avoid harmonic clashes
// - user-recorded melodies can later replace LEAD_A / LEAD_B / BRIDGE_LEAD
// - current TREBLO drum/guitar set passed user browser audition on 2026-09-22
// - FM e-piano C4, fretless C and VCV wavestab0 also passed separate user browser auditions
// - FM/fretless layers are used only where their fixed recorded pitch is harmonically safe
// - VCV wavestab is high-passed and used as a rare transition accent
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

const MASTER = 0.76

const KICK = stack(
  s("tkick*4").speed("1 .998 1.003 .997").gain(.72).lpf(4200).hpf(28),
  s("tkick808*4").gain(.090).lpf(650).hpf(24)
)
const KICK_PEAK = stack(
  s("tkick*4").speed("1 .998 1.003 .997").gain(.76).lpf(5200).hpf(28),
  s("tkick808*4").gain(.100).lpf(720).hpf(24)
)
const KICK_SOFT = stack(
  s("tkick ~ tkick ~").gain(.45).lpf(1900).hpf(30),
  s("tkick808 ~ tkick808 ~").gain(.050).lpf(460)
)
const KICK_BRIDGE = s("tkick ~ ~ ~ tkick ~ ~ ~").gain(.48).lpf(2500).hpf(30)

const CLAP = stack(
  s("~ tclap ~ tclap").gain(.26).hpf(650).lpf(7900),
  s("~ sd ~ sd").bank("AkaiLinn").gain(.060).hpf(500).lpf(9800)
)
const CLAP_PEAK = stack(
  s("~ tclap ~ tclap").gain(.30).hpf(650).lpf(9000),
  s("~ sd ~ sd").bank("AkaiLinn").gain(.082).hpf(480).lpf(11000)
)
const CLAP_LIGHT = s("~ tclap ~ tclap").gain(.16).hpf(850).lpf(6800)

const HATS = stack(
  s("tchh*16")
    .gain(".055 .10 .065 .135 .06 .095 .07 .125 .055 .105 .065 .14 .06 .09 .075 .12")
    .hpf(4300).lpf(12400).swingBy(.18, 8),
  s("hh*8").bank("AkaiLinn")
    .gain(".018 .032 .020 .038 .018 .030 .021 .035")
    .hpf(6500).lpf(14500).swingBy(.18, 4)
)
const HATS_DARK = s("tchh*8")
  .gain(".05 .075 .055 .09 .05 .07 .06 .085")
  .hpf(4300).lpf(8200).swingBy(.18, 4)
const HAT_ACCENT = s("hh:1").bank("RolandTR707")
  .struct("~ ~ t ~ ~ ~ t ~ ~ ~ t ~ ~ ~ t ~")
  .gain(.085).hpf(4600).lpf(11200)
const HAT_ALT = s("hh:1").bank("RolandTR707")
  .struct("~ t ~ ~ ~ t ~ t ~ ~ t ~ ~ t ~ ~")
  .gain(.085).hpf(4700).lpf(11800)
const OPENHAT = s("[~ tohh]*4").gain(.060).hpf(3600).lpf(12000)
const OPENHAT_PEAK = stack(
  s("[~ tohh]*4").gain(.068).hpf(3600).lpf(13000),
  s("[~ oh]*4").bank("RolandTR909").gain(.022).hpf(6000).lpf(14500)
)

const TOM = s("tkick")
  .struct("~ ~ ~ t ~ ~ t ~ ~ ~ ~ t ~ ~ t ~")
  .hpf(250).lpf(560).gain(.28)
const TOM_ALT = s("tkick808")
  .struct("~ ~ t ~ ~ ~ ~ t ~ t ~ ~ ~ ~ t ~")
  .hpf(220).lpf(650).gain(.20)

const PERC_A = stack(
  s("trim").struct("~ ~ t ~ ~ ~ t ~ ~ t ~ ~ ~ ~ t ~")
    .gain(.080).hpf(900).lpf(5500),
  s("tcow").struct("~ ~ ~ t ~ ~ ~ ~ ~ ~ ~ t ~ ~ ~ ~")
    .gain(.014).hpf(850).lpf(3900)
)
const PERC_B = stack(
  s("trim").struct("~ t ~ ~ ~ ~ t ~ ~ t ~ ~ ~ t ~ ~")
    .gain(.075).hpf(950).lpf(6100),
  s("tcow").struct("~ ~ t ~ ~ ~ ~ ~ ~ t ~ ~ ~ ~ ~ ~")
    .gain(.015).hpf(900).lpf(4200)
)
const RIDE = s("rd*8").bank("RolandTR909")
  .gain(.025).hpf(5600).lpf(14200).swingBy(.18, 4)
const CRASH = s("cr").bank("RolandTR909")
  .gain(.065).hpf(1800).lpf(14500).slow(8)

const bassNotesA =
  "<[a1 ~ a1 ~ e2 ~ g1 ~] [a1 ~ c2 ~ e2 ~ g1 ~] [f1 ~ f1 ~ c2 ~ e2 ~] [g1 ~ d2 ~ g1 ~ e2 ~]>"
const bassNotesB =
  "<[a1 ~ e2 a1 ~ g1 e2 ~] [a1 ~ c2 e2 ~ g1 e2 ~] [f1 ~ c2 f1 ~ e2 c2 ~] [g1 ~ d2 g1 ~ e2 d2 ~]>"
const bassNotesPeak =
  "<[a1 e2 a1 ~ g1 e2 a1 ~] [a1 c2 e2 ~ g1 e2 c2 ~] [f1 c2 f1 ~ e2 c2 f1 ~] [g1 d2 g1 ~ e2 d2 g1 ~]>"

const BASS_A = stack(
  note(bassNotesA).s("sawtooth").attack(.004).decay(.14).sustain(.07).release(.05)
    .lpf(760).lpq(1.15).hpf(38).gain(.215),
  note(bassNotesA).s("sine").attack(.003).decay(.13).sustain(.05).release(.045)
    .lpf(185).gain(.058)
)
const BASS_B = stack(
  note(bassNotesB).s("sawtooth").attack(.004).decay(.13).sustain(.06).release(.045)
    .lpf(850).lpq(1.25).hpf(38).gain(.225),
  note(bassNotesB).s("sine").lpf(190).gain(.060)
)
const BASS_PEAK = stack(
  note(bassNotesPeak).s("sawtooth").attack(.003).decay(.11).sustain(.05).release(.04)
    .lpf(980).lpq(1.35).hpf(40).gain(.230),
  note(bassNotesPeak).s("sine").lpf(195).gain(.062)
)
const BASS_BRIDGE = note("<a1 ~ ~ e2 f1 ~ ~ c2 c2 ~ ~ g1 g1 ~ e2 ~>")
  .s("sawtooth").attack(.008).decay(.18).sustain(.06).release(.08)
  .lpf(560).hpf(38).gain(.17)

const chordNotesA =
  "<[a3,c4,e4,g4] [f3,a3,c4,e4] [c4,e4,g4,b4] [g3,b3,d4,e4]>"
const chordNotesB =
  "<[c4,e4,g4,a4] [a3,c4,e4,f4] [e4,g4,b4,c5] [b3,d4,e4,g4]>"
const chordNotesHigh =
  "<[e4,g4,a4,c5] [c4,e4,f4,a4] [g4,b4,c5,e5] [d4,e4,g4,b4]>"

const CHORDS_A = stack(
  note(chordNotesA).s("piano").clip(.42).hpf(190).lpf(8600).room(.12).gain(.050),
  note(chordNotesA).s("triangle").attack(.008).decay(.29).sustain(.045).release(.20)
    .hpf(180).lpf(3900).gain(.026)
)
const CHORDS_B = stack(
  note(chordNotesB).s("piano").clip(.38).hpf(200).lpf(9300).room(.13).gain(.052),
  note(chordNotesB).s("triangle").attack(.008).decay(.27).sustain(.04).release(.19)
    .hpf(180).lpf(4200).gain(.025)
)
const CHORDS_HIGH = note(chordNotesHigh)
  .s("piano").clip(.28).hpf(360).lpf(10800).room(.15).gain(.030)
const CHORDS_BRIDGE = note(chordNotesA)
  .s("piano").clip(.70).hpf(180).lpf(5200).room(.24).gain(.038)

const STAB_A = note(
  "<[~ [a4,c5,e5] ~ ~] [~ [f4,a4,c5] ~ ~] [~ [c5,e5,g5] ~ ~] [~ [g4,b4,d5] ~ ~]>"
).s("piano").clip(.14).hpf(520).lpf(9400).gain(.030)

const STAB_B = note(
  "<[~ ~ [a4,c5,e5] ~] [~ [f4,a4,c5] ~ ~] [[c5,e5,g5] ~ ~ ~] [~ ~ [g4,b4,e5] ~]>"
).s("piano").clip(.12).hpf(560).lpf(10000).gain(.032)

const GUITAR_A = s("<tgtr1 tgtr2 tgtr1 tgtr2>")
  .struct("~ t ~ ~ ~ ~ t ~").hpf(260).lpf(7600).room(.07).gain(.050)
const GUITAR_B = s("<tgtr2 tgtr3 tgtr1 tgtr4>")
  .struct("~ ~ t ~ ~ t ~ ~").hpf(280).lpf(8200).room(.08).gain(.052)
const GUITAR_PEAK = stack(
  GUITAR_A,
  s("<tgtr3 tgtr4 tgtr3 tgtr4>")
    .struct("~ ~ ~ t ~ ~ t ~").hpf(380).lpf(9800).gain(.025)
)


const EP_TINE_A = s("<epc4 epc4 epc4 ~>")
  .struct("~ t ~ ~ ~ ~ t ~")
  .gain(.034).hpf(700).lpf(9200).room(.08)

const EP_TINE_B = s("<epc4 ~ epc4 ~>")
  .struct("~ ~ t ~ ~ t ~ ~")
  .gain(.036).hpf(760).lpf(9800).room(.09)

const FRETLESS_GHOST = s("<~ ~ fbc ~>")
  .struct("~ ~ t ~ ~ ~ ~ t")
  .gain(.052).hpf(45).lpf(1800)

const FRETLESS_GHOST_ALT = s("<~ ~ fbc ~>")
  .struct("~ t ~ ~ ~ ~ t ~")
  .gain(.045).hpf(50).lpf(1600)

const VCV_ACCENT = s("<~ ~ ~ vstab>")
  .struct("~ ~ ~ ~ ~ ~ t ~")
  .gain(.085).hpf(900).lpf(6800).room(.08)

const LEAD_A = note(
  "<[~ ~ e5 ~] [~ c5 ~ e5] [g5 ~ e5 ~] [~ d5 ~ b4]>"
).s("triangle").attack(.010).decay(.16).sustain(.03).release(.10)
  .hpf(340).lpf(5200).room(.12).delay(.06).delaytime(.369).delayfeedback(.18).gain(.026)

const LEAD_B = note(
  "<[~ a4 c5 ~] [e5 ~ ~ c5] [~ g4 c5 e5] [d5 ~ b4 ~]>"
).s("sawtooth").attack(.008).decay(.14).sustain(.022).release(.08)
  .hpf(360).lpf(4700).room(.10).delay(.065).delaytime(.369).delayfeedback(.20).gain(.021)

const BRIDGE_LEAD = note(
  "<[a4 ~ ~ e5] [~ c5 ~ ~] [g4 ~ b4 ~] [~ d5 ~ e5]>"
).s("sine").attack(.08).decay(.32).sustain(.08).release(.26)
  .hpf(320).lpf(3600).room(.20).gain(.020)

const LEAD_PEAK = stack(
  LEAD_A,
  note("<[~ ~ a5 ~] [~ g5 ~ e5] [c6 ~ g5 ~] [e5 ~ d5 ~]>")
    .s("sine").attack(.016).decay(.20).sustain(.025).release(.14)
    .hpf(620).lpf(6500).room(.15).delay(.045).delaytime(.246).delayfeedback(.14).gain(.014)
)

const PAD = stack(
  note("<[a4,e5] [f4,c5] [c5,g5] [g4,d5]>")
    .s("sine").attack(.55).decay(.50).sustain(.26).release(.70)
    .hpf(320).lpf(3200).room(.20).gain(.014),
  note("<e5 c5 g5 d5>")
    .s("triangle").attack(.65).decay(.55).sustain(.18).release(.75)
    .hpf(650).lpf(4300).room(.21).gain(.007)
)

const I1 = stack(CHORDS_BRIDGE, PAD)
const I2 = stack(KICK_SOFT, HATS_DARK, CHORDS_BRIDGE, PAD)
const I3 = stack(KICK_SOFT, HATS_DARK, BASS_A, CHORDS_A)
const I4 = stack(KICK, CLAP_LIGHT, HATS, HAT_ACCENT, BASS_A, CHORDS_A)

const D1 = stack(KICK, CLAP, HATS, HAT_ACCENT, PERC_A, BASS_A, CHORDS_A)
const D2 = stack(KICK, CLAP, HATS, HAT_ACCENT, OPENHAT, PERC_A, BASS_A, CHORDS_A, GUITAR_A, EP_TINE_A)
const D3 = stack(KICK, CLAP, HATS, HAT_ALT, OPENHAT, TOM, PERC_B, BASS_B, CHORDS_A, STAB_A, GUITAR_A, FRETLESS_GHOST)
const D4A = stack(KICK, CLAP, HATS, HAT_ALT, OPENHAT, TOM_ALT, PERC_B, BASS_B, CHORDS_B, STAB_B, GUITAR_B, EP_TINE_B, LEAD_A)
const D4B = stack(D4A, VCV_ACCENT)
const D5 = stack(KICK_SOFT, CLAP_LIGHT, HATS_DARK, BASS_B, CHORDS_B, GUITAR_A, LEAD_A)
const D6 = stack(KICK_PEAK, CLAP, HATS, HAT_ALT, OPENHAT_PEAK, TOM, TOM_ALT, PERC_B, BASS_B, CHORDS_B, STAB_B, GUITAR_B, EP_TINE_B, LEAD_A, VCV_ACCENT)

const C1 = stack(KICK_PEAK, CLAP_PEAK, HATS, HAT_ALT, OPENHAT_PEAK, TOM, PERC_B, BASS_PEAK, CHORDS_B, CHORDS_HIGH, STAB_A, GUITAR_A, EP_TINE_A, FRETLESS_GHOST, LEAD_A)
const C2 = stack(KICK_PEAK, CLAP_PEAK, HATS, HAT_ALT, OPENHAT_PEAK, RIDE, TOM_ALT, PERC_B, BASS_PEAK, CHORDS_B, CHORDS_HIGH, STAB_B, GUITAR_B, EP_TINE_B, FRETLESS_GHOST_ALT, LEAD_B, PAD)
const C3 = stack(KICK, HATS_DARK, OPENHAT, BASS_B, CHORDS_BRIDGE, GUITAR_A, BRIDGE_LEAD, PAD)
const C4A = stack(KICK_PEAK, CLAP_PEAK, HATS, HAT_ALT, OPENHAT_PEAK, RIDE, TOM, TOM_ALT, PERC_B, BASS_PEAK, CHORDS_B, CHORDS_HIGH, STAB_B, GUITAR_PEAK, EP_TINE_A, LEAD_PEAK, PAD)
const C4B = stack(C4A, CRASH, VCV_ACCENT)

const B1 = stack(KICK_BRIDGE, HATS_DARK, BASS_BRIDGE, CHORDS_BRIDGE, BRIDGE_LEAD, PAD)
const B2 = stack(KICK_BRIDGE, HATS_DARK, HAT_ACCENT, BASS_BRIDGE, CHORDS_BRIDGE, GUITAR_A, FRETLESS_GHOST, BRIDGE_LEAD)
const B3 = stack(KICK, CLAP_LIGHT, HATS_DARK, HAT_ACCENT, BASS_A, CHORDS_A, STAB_A, GUITAR_A, EP_TINE_A)
const B4A = stack(KICK_PEAK, CLAP, HATS, HAT_ALT, OPENHAT, TOM_ALT, PERC_A, BASS_B, CHORDS_B, STAB_B, GUITAR_B, LEAD_B)
const B4B = stack(B4A, EP_TINE_B, VCV_ACCENT)

const O1A = stack(KICK, CLAP, HATS, HAT_ACCENT, OPENHAT, PERC_A, BASS_A, CHORDS_A, STAB_A, GUITAR_A, LEAD_A)
const O1B = stack(O1A, EP_TINE_A)
const O2 = stack(KICK, CLAP, HATS, HAT_ACCENT, PERC_A, BASS_A, CHORDS_A, STAB_A, GUITAR_A)
const O3 = stack(KICK_SOFT, CLAP_LIGHT, HATS_DARK, BASS_BRIDGE, CHORDS_BRIDGE, GUITAR_A)
const O4 = stack(KICK_BRIDGE, HATS_DARK, CHORDS_BRIDGE, PAD)

arrange(
  [4, I1], [4, I2], [4, I3], [4, I4],

  [4, D1], [4, D2], [4, D3],
  [2, D4A], [2, D4B],
  [4, D5], [4, D6],

  [8, C1], [8, C2], [4, C3],
  [2, C4A], [2, C4B],

  [4, B1], [4, B2], [4, B3],
  [2, B4A], [2, B4B],

  [2, O1A], [2, O1B],
  [4, O2], [4, O3], [4, O4]
).gain(MASTER)
