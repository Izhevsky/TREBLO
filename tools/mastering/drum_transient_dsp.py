#!/usr/bin/env python3
"""TREBLO v2.3: stereo-linked, bounded, onset-aware *spectral proxy* delta.

Not neural isolation, NOT new drums. The caller makes an exact-reconstruction
STFT pseudo-stem split of the existing drums stem. The only change is a small,
attack-aware gain delta applied to those proxies and mixed into the ORIGINAL
unlimited signal through original + (processed - original) arithmetic.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy.ndimage import gaussian_filter1d

@dataclass(frozen=True)
class Profile:
    kick_body_db: float = 0.40
    kick_attack_db: float = 0.13
    hats_body_db: float = 0.36
    hats_attack_db: float = 0.38
    clap_body_db: float = -0.44
    clap_attack_db: float = -0.18
    cymbal_body_db: float = 0.10
    cymbal_attack_db: float = 0.0

    def validate(self):
        for value in vars(self).values():
            if not np.isfinite(value) or not -1.25 <= value <= 1.25:
                raise ValueError('Unsafe or non-finite pseudo-stem gain')


def onset_envelope(audio: np.ndarray, sr: int, *, hop_seconds: float=0.005) -> np.ndarray:
    """Per-sample linked envelope in [0,1], stable for mono-compatible stereo.

    Based on short vs long RMS, with a frame-energy gate to avoid boosting
    quiet tails/noise. Both channels always share the exact same gain.
    """
    s=np.asarray(audio, dtype=np.float64)
    if s.ndim != 2 or s.shape[1] != 2 or s.shape[0] < 1024 or sr < 8000:
        raise ValueError('Expected >=1024 finite stereo samples')
    if not np.isfinite(s).all():raise ValueError('Nonfinite samples')
    hop=max(1,int(round(sr*hop_seconds)))
    n=len(s)
    # Frame energy average; 2 channels treated symmetrically.
    ix=np.arange(0,n,hop)
    energy=np.mean(s[:len(ix)*hop].reshape(-1,hop,2)**2,axis=(1,2)) if n%hop==0 else None
    if energy is None:
        energy=np.array([np.mean(s[i:min(n,i+hop)]**2) for i in ix])
    short=np.sqrt(np.maximum(gaussian_filter1d(energy,1.6,mode='nearest'),0))
    long=np.sqrt(np.maximum(gaussian_filter1d(energy,20.0,mode='nearest'),0))
    peak=float(np.max(long))
    if peak<1e-9:return np.zeros(n, dtype=np.float64)
    novelty=np.clip((short/(long+1e-9)-1.0)/0.85,0.0,1.0)
    # Soft activity gate: downweight unimportant hiss and near-silence.
    activity=np.clip((short/peak-0.017)/0.13,0,1)
    # Smooth step-on envelopes to avoid gain discontinuities on attacks.
    frame=np.clip(gaussian_filter1d(novelty*activity,1.0),0,1)
    return np.interp(np.arange(n),ix,frame,left=frame[0],right=frame[-1])


def linked_delta(parts:dict[str,np.ndarray],sr:int,profile:Profile=Profile()) -> np.ndarray:
    """Signal delta to be ADDED to the unlimited base, no double layering."""
    profile.validate()
    expected=('kick','hats','snare_clap','cymbals')
    shapes={np.asarray(parts[k]).shape for k in expected}
    if len(shapes)!=1:raise ValueError('Inconsistent pseudo-stem shapes')
    n,ch=shapes.pop()
    if ch!=2:raise ValueError('Stereo only')
    out=np.zeros((n,2),dtype=np.float64)
    gains={
        'kick':(profile.kick_body_db,profile.kick_attack_db),
        'hats':(profile.hats_body_db,profile.hats_attack_db),
        'snare_clap':(profile.clap_body_db,profile.clap_attack_db),
        'cymbals':(profile.cymbal_body_db,profile.cymbal_attack_db)
    }
    for kind,(body,attack) in gains.items():
        s=np.asarray(parts[kind],dtype=np.float64)
        if not np.isfinite(s).all():raise ValueError('Nonfinite proxy')
        if body == 0 and attack == 0:continue
        env=onset_envelope(s,sr) if attack else 0.0
        gain_db=body+attack*env
        # Linked stereo gain; no independent left/right operations.
        out += s * (np.power(10.0,gain_db/20.0)[:,None]-1.0) if isinstance(gain_db,np.ndarray) else s * (10**(gain_db/20.0)-1.0)
    return out
