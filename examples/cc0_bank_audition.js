// TREBLO CC0 bank audition — 122 BPM, one cycle = one bar
samples('github:Izhevsky/TREBLO')
setcpm(122/4)

const kick = s('<lh_tr808_kick:0 lh_tr808_kick:1>*4')
  .gain(.72).lpf(2400).shape(.08)

const clap = s('~ lh_tr808_clap ~ lh_tr808_clap')
  .gain(.32).hpf(420).lpf(6100).late(.006).room(.08)

const hats = s('<[lh_tr808_hat_closed ~ lh_tr808_hat_closed lh_tr808_hat_closed ~ lh_tr808_hat_closed lh_tr808_hat_closed ~] [lh_tr808_hat_closed ~ lh_tr808_hat_closed ~ lh_tr808_hat_closed lh_tr808_hat_closed ~ lh_tr808_hat_closed]>')
  .gain('.12 .07 .16 .09 .08 .14 .10 .07').hpf(2600).lpf(8200).late(.008).pan(.56)

const openHat = s('~ lh_tr808_hat_open:1 ~ lh_tr808_hat_open:0 ~ lh_tr808_hat_open:1 ~ lh_tr808_hat_open:2')
  .gain(.11).hpf(2300).lpf(7200).late(.005).pan(.43)

const rim = s('<[~ ~ lh_tr808_rim ~ ~ ~ ~ lh_tr808_rim] [~ lh_tr808_rim ~ ~ ~ ~ lh_tr808_rim ~]>')
  .gain(.10).lpf(3900).late(.012).pan(.36)

// All bass recordings are tuned to C. speed ratios transpose C2 to E2/C2/A1/B1.
const bass = s('<lh_fretless_c:3 lh_fretless_c:0 lh_fretless_c:3 lh_fretless_c:1>')
  .speed('<1.259921 1 .840896 .943874>')
  .gain(.34).lpf(920).hpf(35).decay(.18).sustain(0).release(.05)

const stab = s('<~ lh_wavestab_vcv:0 ~ lh_wavestab_vcv:1>')
  .speed('<.749154 .840896 .943874 1>')
  .gain(.13).hpf(260).lpf(2100).room(.16).roomsize(1.5).late(.007)

stack(kick, clap, hats, openHat, rim, bass, stab)
