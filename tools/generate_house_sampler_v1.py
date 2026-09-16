import math, os, wave
from pathlib import Path
import numpy as np
from scipy.signal import butter, sosfilt

SR = 32000
BPM = 122
BEAT = 60 / BPM
BAR = 4 * BEAT
N = int(round(4 * BAR * SR))
OUT = Path('loops/house_sampler_v1')
OUT.mkdir(parents=True, exist_ok=True)


def filt(x, cutoff, btype='low', order=2):
    sos = butter(order, cutoff / (SR / 2), btype=btype, output='sos')
    return sosfilt(sos, x, axis=0)


def lp1(x, cutoff):
    a = math.exp(-2 * math.pi * cutoff / SR)
    y = np.zeros_like(x)
    if x.ndim == 1:
        p = 0.0
        for i, v in enumerate(x):
            p = (1-a) * v + a * p
            y[i] = p
    else:
        p = np.zeros(x.shape[1], dtype=np.float64)
        for i in range(len(x)):
            p = (1-a) * x[i] + a * p
            y[i] = p
    return y


def add(buf, sig, sec, gain=1.0, pan=0.5):
    start = int(sec * SR)
    if sig.ndim == 1:
        sig = np.column_stack([sig, sig])
    end = min(len(buf), start + len(sig))
    if start >= len(buf):
        return
    s = sig[:end-start].copy()
    s[:,0] *= math.cos(pan * math.pi / 2) * gain
    s[:,1] *= math.sin(pan * math.pi / 2) * gain
    buf[start:end] += s


def kick():
    dur=.45; nn=int(dur*SR); t=np.arange(nn)/SR
    f=47 + (115-47)*np.exp(-t*22)
    ph=2*np.pi*np.cumsum(f)/SR
    env=np.exp(-t*9.5)
    rng=np.random.default_rng(1)
    click=filt(rng.standard_normal(nn),2500,'high',1)*np.exp(-t*80)*.18
    return np.tanh((np.sin(ph)*env + click)*1.35)*.82


def clap(seed=2):
    dur=.32; nn=int(dur*SR); t=np.arange(nn)/SR
    rng=np.random.default_rng(seed)
    noise=filt(rng.standard_normal(nn),800,'high',2)
    env=np.zeros(nn)
    for d,a in [(0,.85),(.018,.68),(.036,.55),(.065,.45)]:
        j=int(d*SR); env[j:] += a*np.exp(-np.arange(nn-j)/SR*26)
    return np.tanh((noise*env*.24 + np.sin(2*np.pi*185*t)*np.exp(-t*18)*.14)*1.2)


def hat(seed=3, openhat=False):
    dur=.35 if openhat else .09; nn=int(dur*SR); t=np.arange(nn)/SR
    rng=np.random.default_rng(seed)
    noise=filt(rng.standard_normal(nn),5500,'high',1)
    env=np.exp(-t*(10 if openhat else 55))
    metal=(np.sin(2*np.pi*7050*t)+.6*np.sin(2*np.pi*8850*t))*.08
    return (noise*.13+metal)*env


def rim():
    nn=int(.12*SR); t=np.arange(nn)/SR
    x=(np.sin(2*np.pi*760*t)+.6*np.sin(2*np.pi*1280*t))*np.exp(-t*45)
    return np.tanh(x*1.2)*.32


def perc(freq=360, seed=4):
    nn=int(.16*SR); t=np.arange(nn)/SR; rng=np.random.default_rng(seed)
    x=np.sin(2*np.pi*(freq+40*np.exp(-t*25))*t)*np.exp(-t*22)
    x += filt(rng.standard_normal(nn),2500,'high',1)*np.exp(-t*35)*.05
    return np.tanh(x*1.4)*.35


def fm_note(midi, dur=.75, vel=.5):
    nn=int(dur*SR); t=np.arange(nn)/SR; f=440*2**((midi-69)/12)
    mod=np.sin(2*np.pi*f*2*t); idx=2.3*np.exp(-t*2.4)+.55
    a=np.sin(2*np.pi*f*t+idx*mod)+.16*np.sin(2*np.pi*f*2*t)
    b=np.sin(2*np.pi*f*1.0018*t+(idx*.85)*np.sin(2*np.pi*f*2.002*t))
    env=(1-np.exp(-t*65))*np.exp(-t*2.5)
    return (a*.72+b*.28)*env*vel


def analog_note(midi, dur=1.2, vel=.3):
    nn=int(dur*SR); t=np.arange(nn)/SR; f=440*2**((midi-69)/12)
    ph=(f*t)%1; saw=2*ph-1; tri=2*np.abs(2*ph-1)-1
    x=lp1((.58*saw+.42*tri)*(1-np.exp(-t*12))*np.exp(-t*.9),2400)
    return x*vel


def delay(buf, sec, wet=.14, fb=.18):
    out=buf.copy(); d=int(sec*SR)
    for k,g in [(1,wet),(2,wet*fb),(3,wet*fb*fb)]:
        o=d*k
        if o < len(buf):
            out[o:,0] += buf[:-o,1]*g
            out[o:,1] += buf[:-o,0]*g
    return out


def glue(x, drive=1.2):
    x=np.tanh(x*drive); m=np.max(np.abs(x))+1e-9
    return x*(.95/m) if m>.95 else x


def drum_loop(v=0):
    buf=np.zeros((N,2),np.float32); k=kick(); c=clap(2+v); r=rim(); oh=hat(77+v,True)
    hs=[hat(20+i+v*9) for i in range(8)]
    ps=[perc(f,30+i) for i,f in enumerate([300,420,520])]
    swing=.028 if v==0 else .038
    for b in range(4):
        base=b*BAR
        for q in range(4): add(buf,k,base+q*BEAT,.84 if q==0 else .78,.5)
        if v==1 and b in (1,3): add(buf,k,base+3.5*BEAT,.34,.5)
        for q in (1,3): add(buf,c,base+q*BEAT,.48,.5)
        for st in range(8):
            pos=base+st*BEAT/2+(swing if st%2 else 0)
            g=[.16,.24,.17,.29,.15,.25,.18,.31][st]
            add(buf,hs[st],pos,g,.44+.12*(st%2))
        for q in (.5,2.5): add(buf,oh,base+q*BEAT+swing,.11,.58 if q<2 else .42)
        seq=[(1.5,0,.14,.31),(2.75,1,.12,.68),(3.5,2,.10,.38)] if v==0 else [(0.75,1,.11,.68),(1.5,0,.13,.31),(2.25,2,.10,.64),(3.25,1,.12,.36)]
        for q,i,g,p in seq: add(buf,ps[i],base+q*BEAT+(swing if int(q*2)%2 else 0),g,p)
        if v==1 and b in (1,3): add(buf,r,base+3.75*BEAT,.16,.35)
    return glue(filt(buf,35,'high',1),1.25)


CHORDS=[[60,63,67,70,74],[56,60,63,67,70],[53,56,60,63,67],[55,59,62,65,68]]

def keys_loop(v=0):
    buf=np.zeros((N,2),np.float32)
    for b,ch in enumerate(CHORDS):
        hits=[.5,1.75,3.0] if v==0 else [.25,1.5,2.25,3.5]
        for hi,h in enumerate(hits):
            vv=.18 if hi==0 else (.13 if hi==1 else .16)
            for j,m in enumerate(ch):
                add(buf,fm_note(m,.70 if v==0 else .56,vv*(.92+.05*j)),b*BAR+h*BEAT,1,.38+.24*j/(len(ch)-1))
        if v==1 and b in (1,3):
            for j,m in enumerate([ch[-1]+12,ch[-2]+12]): add(buf,fm_note(m,.42,.09),b*BAR+(3.75+j*.12)*BEAT,1,.68-.25*j)
    buf=filt(buf,150,'high',1); buf=lp1(buf,6000); return glue(delay(buf,BEAT*.75,.12,.16),1.08)


def synth_loop(v=0):
    buf=np.zeros((N,2),np.float32)
    motifs=[[(.5,72,.75),(1.5,75,.35),(2.25,79,.45),(3.25,77,.55)],[(.25,68,.55),(1.25,72,.45),(2.5,75,.70),(3.5,70,.35)],[(.5,67,.50),(1.75,72,.65),(2.75,75,.40),(3.25,79,.40)],[(.25,71,.40),(1,74,.35),(2,77,.50),(3,80,.70)]]
    if v:
        motifs=[[(.25,79,.40),(1,77,.55),(2,75,.40),(3.25,72,.70)],[(.5,75,.45),(1.5,72,.55),(2.75,70,.55)],[(.25,72,.40),(1,75,.45),(2,79,.65),(3,82,.35)],[(.5,80,.35),(1.25,77,.45),(2.25,74,.55),(3.25,71,.60)]]
    for b,evs in enumerate(motifs):
        for i,(q,m,d) in enumerate(evs): add(buf,analog_note(m,d*BEAT*1.25,.26 if not v else .23),b*BAR+q*BEAT,1,.32+.18*((i+b)%3))
    buf=filt(buf,220,'high',1); buf=lp1(buf,4800 if not v else 3900); return glue(delay(buf,BEAT*.75,.18,.26),1.12)


def save(name, arr):
    pcm=(np.clip(arr,-1,1)*32767).astype('<i2')
    with wave.open(str(OUT/name),'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())

for name,arr in {
    'house_drum_loop_a.wav':drum_loop(0),
    'house_drum_loop_b.wav':drum_loop(1),
    'house_keys_loop_a.wav':keys_loop(0),
    'house_keys_loop_b.wav':keys_loop(1),
    'house_synth_loop_a.wav':synth_loop(0),
    'house_synth_loop_b.wav':synth_loop(1),
}.items(): save(name,arr)

(OUT/'README.md').write_text('''# House Sampler v1\n\nOriginal TREBLO loops generated deterministically for the DUST / MEMORY project.\n\n- Tempo: 122 BPM\n- Length: 4 bars per WAV\n- Sample rate: 32 kHz / 16-bit stereo PCM\n- Sources: original procedural synthesis only; no copyrighted recordings or third-party producer-pack loops\n- Intended use: MPC-style whole-loop layering, chopping, filtering and resampling in Strudel\n- Generated: 2026-09-16\n''', encoding='utf-8')
