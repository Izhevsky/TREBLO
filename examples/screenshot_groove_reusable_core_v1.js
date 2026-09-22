// SCREENSHOT GROOVE — REUSABLE CORE v1
// Promoted from the 96-bar reconstruction branch after positive user feedback.
// This is a compact reusable seed, not the whole arrangement.

setcpm(122 / 4)

let kick = sound("bd:0")
  .bank("RolandTR909")
  .struct("t ~ ~ ~ t ~ ~ ~ t ~ ~ ~ t ~ ~ ~")
  .gain(0.82)
  .lpf(3200)

let tom = sound("bd:0")
  .bank("RolandTR909")
  .struct("~ ~ ~ t ~ ~ t ~ ~ ~ ~ t ~ ~ t ~")
  .hpf(250)
  .lpf(500)
  .gain(0.48)

let rollinghat = sound("hh:0")
  .bank("RolandTR909")
  .struct("t t t t t t t t t t t t t t t t")
  .gain("0.12 0.22 0.15 0.29 0.13 0.20 0.16 0.27 0.12 0.23 0.15 0.30 0.13 0.20 0.17 0.27")
  .hpf(500)
  .lpf(10500)
  .swingBy(0.18, 8)

let hat = sound("hh:1")
  .bank("RolandTR707")
  .struct("~ ~ t ~ ~ ~ t ~ ~ ~ t ~ ~ ~ t ~")
  .gain(0.17)
  .hpf(3500)
  .lpf(9000)

let clap = sound("cp:0")
  .bank("RolandTR707")
  .struct("~ ~ ~ ~ t ~ ~ ~ ~ ~ ~ ~ t ~ ~ ~")
  .gain(0.32)
  .hpf(650)
  .lpf(6200)

stack(kick, tom, rollinghat, hat, clap).gain(.82)
