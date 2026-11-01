#!/usr/bin/env python3
"""TREBLO v2.3; restartable Astra stem-delta / transient-precision master.

Input WAV+stems never overwritten. Independent stages with source hashes in manifest.
DRUM SUBSTEMS ARE SPECTRAL PROXIES, NOT NEURAL INSTRUMENT ISOLATION.
"""
from __future__ import annotations
import argparse, json, time, hashlib, shutil, sys
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import soundfile as sf

from drum_substem_dsp import split_drums
from drum_transient_dsp import linked_delta,Profile
from stem_delta_rework import STEM_NAMES,validate_stems,build_delta_remix
from astra_pedalboard import (sha256,sample_count,shell,scan_loudness,
                               independently_scan_ebur128,master_premaster,
                               convert_float_to_pcm,Config)


def run(original:Path, stemdir:Path, workdir:Path, output:Path, stage:str, overwrite:bool=False):
    original=original.resolve();stemdir=stemdir.resolve()
    workdir.mkdir(parents=True,exist_ok=True)
    output.parent.mkdir(parents=True,exist_ok=True)
    if original.resolve()==output.resolve():raise ValueError('Never overwrite source')
    stems={n:stemdir/f'{n} golden teeth.wav' for n in STEM_NAMES}
    for p in [original,*stems.values()]:
        if not p.exists():raise FileNotFoundError(p)
    fp={'original':sha256(original),**{n:sha256(p) for n,p in stems.items()}}
    manifest=workdir/'source_manifest_v23.json'
    if manifest.exists():
        saved=json.loads(manifest.read_text())
        if saved!=fp:raise RuntimeError('Workdir source hashes changed — refuse stale cache')
    else:
        manifest.write_text(json.dumps(fp,indent=2))
    native=workdir/'original_44100_float.wav'
    baseline=workdir/'baseline_v21_float.wav'
    raw=workdir/'raw_v23_float.wav'
    premaster=workdir/'PREMASTER_float32.wav'
    limited=workdir/'post_limiter_float32.wav'
    stages=('prepare','mix','master') if stage=='all' else (stage,)
    for step in stages:
        if step=='prepare':
            if not native.exists() or overwrite:
                shell(['ffmpeg','-v','error','-nostdin','-y','-i',str(original),
                      '-ar','44100','-ac','2','-c:a','pcm_f32le',str(native)],900)
            qc=validate_stems(native,stems)
            if qc['global_reconstruction_error_db']>-32 or qc['max_window_error_db']>-23:
                raise RuntimeError('Stems mismatch source: prevent bad mix')
            (workdir/'stem_validation.json').write_text(json.dumps(qc,indent=2))
            print('prepare: PASS',qc['global_reconstruction_error_db'],flush=True)
        elif step=='mix':
            if not native.exists() or not (workdir/'stem_validation.json').exists():
                raise RuntimeError('Run --stage prepare first')
            q=json.loads((workdir/'stem_validation.json').read_text())
            n,sr,channels=sample_count(native)
            if sr!=44100 or channels!=2:raise RuntimeError('Wrong grid')
            if not baseline.exists() or overwrite:
                build_delta_remix(native,stems,baseline,n,sr,32768)
            if not raw.exists() or overwrite:
                with sf.SoundFile(baseline) as sfbase,sf.SoundFile(stems['drums']) as sfdrum,\
                     sf.SoundFile(raw,'w',samplerate=sr,channels=2,subtype='FLOAT') as dest:
                    frames=sr*8;margin=round(.60*sr);peak=0.;energy=diffenergy=0.;error=0.
                    for pos in range(0,n,frames):
                        end=min(n,pos+frames);lo=max(0,pos-margin);hi=min(n,end+margin)
                        sfdrum.seek(lo);buf=sfdrum.read(hi-lo,dtype='float64',always_2d=True)
                        parts=split_drums(buf,sr)
                        error=max(error,float(np.max(np.abs(sum(parts.values())-buf))))
                        delta=linked_delta(parts,sr,Profile())[pos-lo:end-lo]
                        y0=sfbase.read(end-pos,dtype='float64',always_2d=True)
                        y=y0+delta
                        if not np.isfinite(y).all():raise RuntimeError('Nonfinite output')
                        peak=max(peak,float(np.max(abs(y))))
                        energy+=float(np.sum(y0*y0));diffenergy+=float(np.sum(delta*delta))
                        dest.write(y.astype('float32'))
                (workdir/'stage3.json').write_text(json.dumps({'raw_peak':peak,
                 'delta_rms_relative_db':float(10*np.log10(diffenergy/energy)),
                 'drum_null_max':error,'frames':n,'sr':sr},indent=2))
            stats=json.loads((workdir/'stage3.json').read_text())
            if not premaster.exists() or overwrite:
                gain=10**(-6/20)/stats['raw_peak']
                shell(['ffmpeg','-v','error','-nostdin','-y','-i',str(raw),
                        '-af',f'volume={gain:.15f}','-c:a','pcm_f32le',str(premaster)],900)
            if sample_count(premaster)!=(n,sr,2):raise RuntimeError('Premaster mismatch')
            print('mix: PASS',stats,flush=True)
        elif step=='master':
            if not premaster.exists():raise RuntimeError('Run --stage mix first')
            n,sr,ch=sample_count(premaster)
            if output.exists() and not overwrite:
                raise FileExistsError('Final output exists; use --overwrite to replace this experimental file only')
            q0=scan_loudness(premaster,'ffmpeg')
            cfg=Config(input=premaster,output=output,target_lufs=-13.7,true_peak_ceiling=-1.4)
            passes=[]
            for i in range(4):
                ceil=-1.55-.16*i
                master_premaster(premaster,limited,cfg,q0['input_i'],ceil)
                candidate=workdir/'candidate_v23.flac'
                convert_float_to_pcm(limited,candidate,'ffmpeg',24)
                final=scan_loudness(candidate,'ffmpeg')
                passes.append({'ceiling':ceil,'final_tp':final['input_tp']})
                if final['input_tp']<=-1.35:break
            else:raise RuntimeError('Cannot satisfy final true-peak ceiling')
            if sample_count(candidate)!=(n,sr,ch):raise RuntimeError('Final grid mismatch')
            if any(sha256(p)!=fp[k] for k,p in [('original',original),*stems.items()]):
                raise RuntimeError('Source changed')
            shutil.copyfile(candidate,output)
            out16=output.with_name(output.stem+'_16bit.flac')
            convert_float_to_pcm(limited,out16,'ffmpeg',16)
            if sample_count(out16)!=(n,sr,ch):raise RuntimeError('16bit grid mismatch')
            report={'version':'TREBLO_v2.3_transient_precision','source_hashes':fp,
             'final_sha256':sha256(output),'final16_sha256':sha256(out16),
             'final_loudnorm_input_fields':final,'independent_lufs':independently_scan_ebur128(output,'ffmpeg'),
             'passes':passes,'dsp_profile':vars(Profile()),'subjective_qc':'AWAITING_USER'}
            output.with_suffix('.qc.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
            print('master: PASS',final,flush=True)
        else:raise ValueError(step)

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--original',type=Path,required=True)
    ap.add_argument('--stemdir',type=Path,required=True)
    ap.add_argument('--workdir',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--stage',choices=['prepare','mix','master','all'],default='all')
    ap.add_argument('--overwrite',action='store_true')
    a=ap.parse_args()
    run(a.original,a.stemdir,a.workdir,a.output,a.stage,a.overwrite)
