#!/usr/bin/env python3
"""TREBLO v2.2 CPU DSP baseline: conservative drum pseudo-stems, no neural model.

Split the supplied REAL drums stem into spectral kick / snare-clap / hat /
cymbal proxies and a complementary residual. The five stems have *exact*
additive reconstruction at sample level, because residual is constructed in
sample domain. Isolation is NOT perfect: frequency overlap and instrument
bleed remain. Never identify these pseudo-stems as real multitracks.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy.signal import stft, istft
from scipy.ndimage import gaussian_filter1d, maximum_filter1d, minimum_filter1d

COMPONENTS = ("kick", "snare_clap", "hats", "cymbals", "residual")


def bell(f, left, right, slope=0.12):
    # Rounded log-frequency envelope: deterministic, smooth, no hard crossover.
    f = np.maximum(f, 1.0)
    def sig(x): return 1.0 / (1.0 + np.exp(-np.clip(x, -60., 60.)))
    return sig(np.log(f/left)/slope) * sig(np.log(right/f)/slope)


def activity(Z, freq, lo, hi):
    mag = np.mean(np.abs(Z), axis=0)
    band = mag[(freq>=lo)&(freq<=hi)]
    env = np.sum(band**2,axis=0) if len(band) else np.zeros(mag.shape[1])
    # Window smoothing approx 20 ms at fs=44.1k, hop=512
    env=gaussian_filter1d(env, 2.0)
    a=minimum_filter1d(env, size=23,mode='nearest')
    b=maximum_filter1d(env,size=23,mode='nearest')
    g=np.clip((env-a)/(b-a+1e-12),0,1)
    return gaussian_filter1d(g,0.9)


def split_drums(audio: np.ndarray, sr: int, nfft=2048, hop=512):
    """(samples,2) -> dict of reconstructed float64 arrays; sum == input."""
    x=np.asarray(audio,dtype=np.float64)
    if x.ndim!=2 or x.shape[1]!=2 or len(x)<nfft or not np.isfinite(x).all():
        raise ValueError("Require finite stereo segment with >=2048 frames")
    f, _, z=stft(x.T, fs=sr, nperseg=nfft, noverlap=nfft-hop,
                   boundary='zeros',padded=True,axis=-1)
    low=activity(z,f,35,210)
    mid=activity(z,f,150,4000)
    high=activity(z,f,5100,15000)
    wk=(0.78*bell(f,30,215)[:,None]*(0.30+0.70*low)[None,:]).astype(np.float64)
    ws=(0.72*(.50*bell(f,145,590)+.75*bell(f,1700,5300))[:,None]*(.30+.70*mid)[None,:])
    wh=(0.77*bell(f,5400,15000)[:,None]*(.24+.76*high)[None,:])
    wc=(0.28*bell(f,4400,17700)[:,None]*(.70-.35*high)[None,:])
    weights=np.stack([wk,ws,wh,wc],axis=0)
    s=np.sum(weights,axis=0)
    # Sum of component TF masks <=0.92. Residual catches ALL unassigned audio.
    weights*=np.minimum(1.0,0.92/(s+1e-12))[None,:,:]
    outputs={}
    for i,name in enumerate(COMPONENTS[:-1]):
        _,wav=istft(z*weights[i][None,:,:],fs=sr,nperseg=nfft,
                    noverlap=nfft-hop,boundary=True,input_onesided=True,time_axis=-1,freq_axis=-2)
        outputs[name]=wav.T[:len(x)].astype(np.float64)
    outputs['residual']=x-sum(outputs.values())
    if max(abs((sum(outputs.values())-x)).ravel())>5e-10:
        raise AssertionError("Non-reconstructing drum split")
    return outputs


def remix_delta(parts, kick_db=.48, hats_db=1.0, clap_db=-.60, cymbal_db=.25):
    """Only *deltas*: never overlay new copies of unprocessed drum hits."""
    db_to_delta=lambda d: 10**(d/20)-1
    return (db_to_delta(kick_db)*parts['kick']+
            db_to_delta(hats_db)*parts['hats']+
            db_to_delta(clap_db)*parts['snare_clap']+
            db_to_delta(cymbal_db)*parts['cymbals'])


@dataclass(frozen=True)
class DspProfile:
    kick_db: float=.48
    hats_db: float=1.0
    clap_db: float=-.60
    cymbal_db: float=.25
    def __post_init__(self):
        if max(abs(v) for v in vars(self).values())>2:
            raise ValueError('Unsafe >2dB adjustment for ambiguous pseudo-stems')