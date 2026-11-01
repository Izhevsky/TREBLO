#!/usr/bin/env python3
"""TREBLO v2.6: genuine DrumSep checkpoint integration smoke (synthetic music ONLY).

Never uploads the user's Golden Teeth audio. The test downloads official
SHA-verified model artifacts if and only if --allow-download is specified.
Does NOT produce a mastered commercial/release track or claim stem purity.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import json
import os
import hashlib
import tempfile
import numpy as np
import soundfile as sf
from drumsep_6stem_float_bridge import run, sha256


def synthetic_drums(sr: int = 44100, seconds: float = 2.0) -> np.ndarray:
    if sr != 44100 or not (1.0 <= seconds <= 12):
        raise ValueError("Smoke test expects 44.1 kHz, 1-12 seconds")
    n = round(sr * seconds)
    samples = np.zeros((n, 2), dtype=np.float64)
    # Original synthetic transients, no copyrighted recordings.
    for k, onset in enumerate(np.arange(0.12, seconds - 0.12, 0.5)):
        i = round(float(onset) * sr)
        size = min(round(sr * 0.18), n-i)
        t = np.arange(size) / sr
        kick = np.sin(2 * np.pi * (68 * t + 42 * (1 - np.exp(-t*26)) / 26)) * np.exp(-t * 25)
        samples[i:i+size, :] += (0.25 * kick)[:, None]
        # Deterministic hi-hat burst from independent left/right noise.
        if k < 3:
            ih = min(n - 1, i + round(0.22 * sr))
            length = min(round(0.055*sr),n-ih)
            rng = np.random.default_rng(780 + k)
            noise = rng.normal(0,0.018,(length,2)) * np.exp(-np.arange(length)[:,None] / (sr*.017))
            samples[ih:ih+length] += noise
    return samples.astype('float32')


def inspect_result(source: Path, target: Path) -> dict:
    with sf.SoundFile(source) as f:
        frames, sr, ch = f.frames,f.samplerate,f.channels
    p=target/source.stem
    expected=('kick','snare','toms','hh','cymbals')
    paths=[p/(s+'.wav') for s in expected]
    if any(not path.is_file() for path in paths):
        raise RuntimeError('Real model did not produce expected stem files')
    energies={}; predicted=np.zeros((frames,2),dtype=np.float64)
    for label,path in zip(expected,paths):
        with sf.SoundFile(path) as f:
            if (f.frames,f.samplerate,f.channels,f.subtype)!=(frames,sr,ch,'FLOAT'):
                raise RuntimeError(f'Bad grid/subtype: {path}')
        sig,_=sf.read(path,always_2d=True,dtype='float64')
        if not np.isfinite(sig).all():raise RuntimeError('Invalid samples')
        energies[label]=float(np.mean(sig*sig))
        predicted+=sig
    orig,_=sf.read(source,always_2d=True,dtype='float64')
    error=orig-predicted
    total=float(np.sum(orig*orig))
    q={
      'status':'REAL_CHECKPOINT_INFERENCE_COMPLETED',
      'input_sha256':sha256(source),
      'source_type':'SYNTHETIC_2_SECOND_AUDIO_NOT_USER_MUSIC',
      'model':'drumsep-6stem',
      'total_frames':frames,'sr':sr,
      'energy_by_stem':energies,
      'sum_reconstruction_error_db':float(10*np.log10((np.sum(error*error)+1e-30)/(total+1e-30))),
      'stem_sha256':{k:sha256(p) for k,p in zip(expected,paths)},
      'notes':'Does not demonstrate real-world separation quality, only working model inference; no user audio uploaded'
    }
    if not any(v > 1e-13 for v in energies.values()):
        raise RuntimeError('Model returned silence; real smoke fails')
    if not np.isfinite(q['sum_reconstruction_error_db']):
        raise RuntimeError('Nonfinite reconstruction metric')
    return q


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--workdir',type=Path,required=True)
    ap.add_argument('--cache-dir',type=Path,required=True)
    ap.add_argument('--device',choices=['cpu','cuda'],default='cpu')
    ap.add_argument('--allow-download',action='store_true',help='Explicitly permit fetching the public checkpoint; no input uploads')
    a=ap.parse_args()
    w=a.workdir.resolve();w.mkdir(parents=True,exist_ok=True)
    src=w/'SYNTHETIC_DRUMS_ONLY.wav'
    if src.exists():raise FileExistsError('Refusing to overwrite existing input')
    sf.write(src,synthetic_drums(),44100,subtype='FLOAT')
    before=sha256(src)
    result=run(src,w/'real_stems',a.cache_dir,device=a.device,allow_download=a.allow_download)
    if before!=sha256(src):raise RuntimeError('Source changed')
    q=inspect_result(src,w/'real_stems')
    q['run_report']=result
    p=w/'real_smoke_qc.json';p.write_text(json.dumps(q,indent=2,ensure_ascii=False),encoding='utf-8')
    print('REAL_DRUMSEP_SMOKE_PASS:',str(p))
    print(json.dumps({k:q[k] for k in ['status','total_frames','sr','sum_reconstruction_error_db','energy_by_stem']},indent=2))

if __name__=='__main__':main()