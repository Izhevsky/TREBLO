#!/usr/bin/env python3
"""TREBLO v2.1 — verified aligned stems -> conservative delta remix -> Astra mastering.

Input remains untouched. We refuse poorly matching stems. We never double an
existing stem: output = original + sum(processed_stem - unprocessed_stem).
Requires six complementary aligned WAVs (unused/quiet stems allowed).
This is NOT neural stem separation; it uses provided multitracks.
"""
from __future__ import annotations
from contextlib import ExitStack
from dataclasses import dataclass
from pathlib import Path
import argparse
import hashlib
import json
import math
import os
import shutil
import tempfile

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt
from pedalboard import Pedalboard, PeakFilter, HighShelfFilter

from astra_pedalboard import (sha256, shell, scan_loudness, independently_scan_ebur128,
                              master_premaster, convert_float_to_pcm, sample_count, Config)

STEM_NAMES = ('drums', 'bass', 'other', 'piano', 'guitar', 'vocals')
EFFECTS = {
    'drums': {'kick_db': 0.55, 'lowmid_db': -0.25, 'hat_air_db': 0.48},
    'bass': {'fundamental_db': 0.35, 'boxiness_db': -0.35},
    'other': {'mud_db': -0.40, 'presence_db': 0.28, 'air_db': 0.18, 'high_side_boost': 0.075},
    # Do not change near-empty tracks or add new notes; they are included in QC.
}


def boards():
    return {
        'drums': Pedalboard([
            PeakFilter(cutoff_frequency_hz=65, gain_db=0.55, q=0.85),
            PeakFilter(cutoff_frequency_hz=430, gain_db=-0.25, q=0.80),
            HighShelfFilter(cutoff_frequency_hz=8700, gain_db=0.48, q=0.7)]),
        'bass': Pedalboard([
            PeakFilter(cutoff_frequency_hz=95, gain_db=0.35, q=0.75),
            PeakFilter(cutoff_frequency_hz=320, gain_db=-0.35, q=0.8)]),
        'other': Pedalboard([
            PeakFilter(cutoff_frequency_hz=330, gain_db=-0.40, q=0.85),
            PeakFilter(cutoff_frequency_hz=2900, gain_db=0.28, q=0.9),
            HighShelfFilter(cutoff_frequency_hz=9100, gain_db=0.18, q=0.7)]),
    }


@dataclass(frozen=True)
class StemSettings:
    original: Path
    stems_dir: Path
    output: Path
    target_lufs: float = -13.7
    ceiling_dbtp: float = -1.4
    block_frames: int = 32768
    min_global_reconstruction_db: float = -32.0
    min_local_reconstruction_db: float = -23.0
    keep_premaster: bool = True

    def validate(self):
        if not self.original.is_file(): raise FileNotFoundError(self.original)
        if self.output.suffix.lower() != '.flac': raise ValueError('Output must be FLAC')
        if self.original.resolve() == self.output.resolve(): raise ValueError('Never overwrite source')
        if self.block_frames < 8192: raise ValueError('Block too short')
        if not (-22 <= self.target_lufs <= -8): raise ValueError('Target LUFS outside allowed range')
        if not (-3 <= self.ceiling_dbtp <= -0.5): raise ValueError('Ceiling outside allowed range')
        for name, p in stem_paths(self).items():
            if not p.is_file(): raise FileNotFoundError(p)


def stem_paths(cfg):
    paths = {}
    for name in STEM_NAMES:
        candidates = [cfg.stems_dir / f'{name}.wav',
                      cfg.stems_dir / f'{name} golden teeth.wav']
        paths[name] = next((p for p in candidates if p.is_file()), candidates[0])
    return paths


def prepare_original(cfg, dest: Path, desired_rate: int):
    with sf.SoundFile(cfg.original) as f:
        sr, ch = f.samplerate, f.channels
        if ch != 2 or not len(f): raise ValueError('Original must be nonempty stereo')
        if sr == desired_rate: return cfg.original
    shell(['ffmpeg','-nostdin','-v','error','-y','-i', str(cfg.original),
           '-ar',str(desired_rate),'-ac','2','-c:a','pcm_f32le', str(dest)],900)
    return dest


def _frames_and_rate(paths):
    meta = {}
    for name, path in paths.items(): meta[name] = sample_count(path)
    if len(set(meta.values())) != 1: raise ValueError(f'Stems need identical sample grids: {meta}')
    n, sr, ch = next(iter(meta.values()))
    if ch != 2 or sr not in (44100, 48000): raise ValueError('Require 44.1/48k stereo stems')
    return n, sr


def validate_stems(original: Path, paths, block_frames=65536, local_window_seconds=10):
    n, rate = _frames_and_rate(paths)
    if sample_count(original) != (n, rate, 2):
        raise ValueError(f'Original and stem grids disagree: {sample_count(original)} vs {(n,rate,2)}')
    error_sum = source_sum = cross_sum = stems_sum = 0.0
    local = []
    n_window = local_window_seconds * rate
    with ExitStack() as stack:
        mix = stack.enter_context(sf.SoundFile(original))
        streams = {name: stack.enter_context(sf.SoundFile(p)) for name,p in paths.items()}
        num_processed = 0
        while num_processed < n:
            chunk_n = min(n_window, n-num_processed)
            # Window boundaries are fixed in time, independent of IO block size.
            x = mix.read(chunk_n, always_2d=True, dtype='float64')
            y = np.zeros_like(x)
            for f in streams.values(): y += f.read(len(x), always_2d=True, dtype='float64')
            if not np.isfinite(x).all() or not np.isfinite(y).all(): raise ValueError('NaN/Inf input')
            se = float(np.sum(x*x)); ee = float(np.sum((x-y)**2))
            local.append({'start_sec': round(num_processed/rate,3),
                          'error_db': round(float(10*np.log10((ee+1e-40)/(se+1e-40))),3)})
            error_sum += ee; source_sum += se
            cross_sum += float(np.sum(x*y)); stems_sum += float(np.sum(y*y))
            num_processed += len(x)
    err_db = float(10*np.log10((error_sum+1e-40)/(source_sum+1e-40)))
    corr = float(cross_sum / math.sqrt(source_sum * stems_sum))
    max_err_db = max(x['error_db'] for x in local if x['start_sec'] < n/rate-1)
    return {'global_reconstruction_error_db':err_db, 'max_window_error_db':max_err_db,
            'correlation':corr, 'windows':local, 'frames':n, 'rate':rate}


def build_delta_remix(original, paths, out:Path, nframes:int, rate:int, chunk:int):
    fx = boards()
    states = {name: True for name in fx}
    # 4th order high pass ensures sub never gains artificial stereo width.
    sos = butter(4, 700, btype='highpass', fs=rate, output='sos')
    zi = np.zeros((sos.shape[0],2),dtype=np.float64) # signal is (N,2) with axis=0
    peak = 0.0
    with ExitStack() as stack:
        src = stack.enter_context(sf.SoundFile(original))
        tracks = {name:stack.enter_context(sf.SoundFile(path)) for name,path in paths.items()}
        dst = stack.enter_context(sf.SoundFile(out,'w',samplerate=rate,channels=2,subtype='FLOAT'))
        frames_done=0
        while frames_done < nframes:
            x = src.read(min(chunk,nframes-frames_done), dtype='float64', always_2d=True)
            delta = np.zeros_like(x)
            for name, handle in tracks.items():
                s = handle.read(len(x),dtype='float32',always_2d=True)
                if not np.isfinite(s).all(): raise ValueError(f'Nonfinite stem: {name}')
                if name in fx:
                    edited = np.asarray(fx[name](s.T.copy(), rate, reset=states[name]), dtype=np.float64).T
                    states[name] = False
                    if name == 'other':
                        side = (edited[:,0] - edited[:,1])*0.5
                        filtered, zi = sosfilt(sos, side, zi=zi)
                        # Pure side addition (L += d, R -= d) above 700 Hz.
                        d = 0.075 * filtered
                        edited[:,0] += d
                        edited[:,1] -= d
                    delta += edited - s.astype(np.float64)
            y=x+delta
            if not np.isfinite(y).all(): raise ValueError('Nonfinite output')
            peak = max(peak,float(np.max(np.abs(y))))
            dst.write(y.astype(np.float32))
            frames_done+=len(x)
    return peak


def run(cfg: StemSettings):
    cfg.validate()
    inputs=stem_paths(cfg)
    input_hashes={'original':sha256(cfg.original),**{name:sha256(p) for name,p in inputs.items()}}
    n,rate=_frames_and_rate(inputs)
    cfg.output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='treblo-stems-v21-') as td:
        temp=Path(td)
        original=prepare_original(cfg,temp/'original_converted.wav',rate)
        qc=validate_stems(original,inputs)
        if qc['global_reconstruction_error_db'] > cfg.min_global_reconstruction_db:
            raise ValueError('FAILED reconstruction gate (global): do not process mismatched stems')
        if qc['max_window_error_db'] > cfg.min_local_reconstruction_db:
            raise ValueError('FAILED reconstruction gate (local): verify stems and alignment')
        delta_path=temp/'delta_mix_float32.wav'
        peak=build_delta_remix(original,inputs,delta_path,n,rate,cfg.block_frames)
        if peak < 1e-9: raise ValueError('Empty audio')
        # Astra premaster must have precisely -6dBFS sample peak.
        target=10**(-6/20);gain=target/peak
        premaster=temp/'PREMASTER_float32.wav'
        shell(['ffmpeg','-nostdin','-v','error','-y','-i',str(delta_path),
               '-af',f'volume={gain:.12f}', '-c:a','pcm_f32le',str(premaster)],900)
        if sample_count(premaster)!=(n,rate,2): raise ValueError('Premaster grid mismatch')
        pm=scan_loudness(premaster,'ffmpeg')
        # Use existing transparent Astra final stage with independent TP scan.
        mc=Config(input=premaster,output=cfg.output,target_lufs=cfg.target_lufs,
                  true_peak_ceiling=cfg.ceiling_dbtp)
        attempts=[]
        for j in range(4):
            ceiling=cfg.ceiling_dbtp-0.15-0.15*j
            floating=temp/f'masterfloat_{j}.wav'
            master_premaster(premaster,floating,mc,pm['input_i'],ceiling)
            candidate=temp/'master24.flac'
            convert_float_to_pcm(floating,candidate,'ffmpeg',24)
            measured=scan_loudness(candidate,'ffmpeg')
            attempts.append({'attempt':j+1,'ceiling_dbfs':ceiling,'true_peak_dbtp':measured['input_tp']})
            if measured['input_tp'] <= cfg.ceiling_dbtp+0.05:break
        else: raise RuntimeError(f'Output exceeds TP ceiling: {attempts}')
        if sample_count(candidate)!=(n,rate,2): raise ValueError('Master grid mismatch')
        for role,path in [('original',cfg.original),*inputs.items()]:
            if sha256(path)!=input_hashes[role]: raise RuntimeError(f'Source altered: {role}')
        qc16=temp/'master16.flac'
        convert_float_to_pcm(floating,qc16,'ffmpeg',16)
        if sample_count(qc16)!=(n,rate,2): raise RuntimeError('16-bit master length mismatch')
        os.replace(candidate,cfg.output)
        output16=cfg.output.with_name(cfg.output.stem+'_16bit.flac')
        shutil.copy2(qc16,output16)
        if cfg.keep_premaster:
            shutil.copy2(premaster,cfg.output.with_name(cfg.output.stem+'_PREMASTER_float32.wav'))
    report={
        'engine':'TREBLO_Astra_Stem_Delta_Rework_v2.1',
        'routing':'original_resampled_to_stem_grid + sum(processed_stem - original_stem)',
        'source_files_sha256':input_hashes,'stems_reconstruction_qc':qc,
        'per_stem_processing':EFFECTS,'quality_assurance':{'source_sha256_unchanged':True,
        'frames':n,'sample_rate':rate,'channels':2,'post_limiter_true_peak_dbtp':measured['input_tp'],
        'post_limiter_integrated_lufs':measured['input_i'],'post_limiter_lra':measured['input_lra'],
        'independent_ebur128_lufs':independently_scan_ebur128(cfg.output,'ffmpeg'),
        'subjective_listening':'NOT_PERFORMED'},'processing_notes':{
        'delta_mix_peak_before_premaster':peak,'premaster_gain_db':20*math.log10(gain),
        'limiter_attempts':attempts,'output_sha256':sha256(cfg.output),
        'compatible_16bit_sha256':sha256(output16)}}
    cfg.output.with_suffix('.qc.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    return report


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--original',required=True,type=Path)
    ap.add_argument('--stems-dir',required=True,type=Path)
    ap.add_argument('--output',required=True,type=Path)
    ap.add_argument('--target-lufs',type=float,default=-13.7)
    ap.add_argument('--ceiling-dbtp',type=float,default=-1.4)
    ap.add_argument('--keep-premaster',action=argparse.BooleanOptionalAction,default=True)
    a=ap.parse_args()
    r=run(StemSettings(a.original,a.stems_dir,a.output,a.target_lufs,a.ceiling_dbtp,
                       keep_premaster=a.keep_premaster))
    print(json.dumps({k:v for k,v in r.items() if k!='stems_reconstruction_qc'},indent=2,ensure_ascii=False))

if __name__=='__main__': main()