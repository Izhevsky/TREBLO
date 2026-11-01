#!/usr/bin/env python3
"""TREBLO Astra v2.8: local-only, model-verified neural kick A/B pipeline.

No neural weights supplied or fabricated. No upload of user audio. All source
files remain untouched. Gated neural kick +0...0.35 dB; no changes to neural
hat, cymbal or snare predictions; no auto-promotion to released master.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import tempfile

import numpy as np
import soundfile as sf

from astra_pedalboard import (Config, sha256, sample_count, scan_loudness,
                              master_premaster, convert_float_to_pcm,
                              independently_scan_ebur128)
from neural_kick_guard import build_candidate

MODEL_NAMES = ('kick','snare','toms','hh','cymbals')


def source_preflight(drums: Path, v23_unlimited:Path, v23_master:Path, studio_rework:Path) -> dict:
    files={'drums':Path(drums).resolve(), 'v23_unlimited':Path(v23_unlimited).resolve(),
           'v23_master':Path(v23_master).resolve(), 'studio_rework':Path(studio_rework).resolve()}
    for name,p in files.items():
        if not p.is_file(): raise FileNotFoundError(f'{name}: {p}')
    grids={k:sample_count(v) for k,v in files.items()}
    g=grids['drums']
    if g[1:]!=(44100,2) or g[0]<44100:raise ValueError('Expected existing 44.1k stereo drums, >1 sec')
    if any(x!=g for x in grids.values()):raise ValueError('Source/master WAV or FLAC frames/grid differ. No implicit resampling.')
    with sf.SoundFile(files['v23_unlimited']) as f:
        if f.subtype!='FLOAT':raise ValueError('Must use unlimited float32 mix (not mastered PCM)')
    return {'source_files':{k:str(v) for k,v in files.items()}, 'source_sha256':{k:sha256(v) for k,v in files.items()},
            'frames':g[0], 'sample_rate':g[1], 'channels':g[2], 'duration_seconds':g[0]/g[1],
            'status':'INPUT_READY_WITHOUT_NEURAL_INFERENCE',
            'source_policy':'Never overwrite source or previously approved masters'}


def normalize_float_premaster(unlimited:Path,premaster:Path,block_size=131072):
    if unlimited.resolve()==premaster.resolve():raise ValueError('Overwrite source forbidden')
    if premaster.exists():raise FileExistsError(premaster)
    peak=0.0;grid=sample_count(unlimited)
    with sf.SoundFile(unlimited) as f:
        while True:
            a=f.read(block_size,dtype='float64',always_2d=True)
            if not len(a):break
            if not np.isfinite(a).all():raise ValueError('Nonfinite audio')
            peak=max(peak,float(np.max(np.abs(a))))
    if peak<1e-12:raise ValueError('Silence: cannot normalize')
    gain=10**(-6/20)/peak
    with sf.SoundFile(unlimited) as src, sf.SoundFile(premaster,'w',samplerate=grid[1],channels=2,subtype='FLOAT') as dst:
        while True:
            x=src.read(block_size,dtype='float64',always_2d=True)
            if not len(x):break
            dst.write((x*gain).astype('float32'))
    if sample_count(premaster)!=grid:raise RuntimeError('Premaster frame mismatch')
    return {'sample_peak_before':peak,'static_premaster_gain_db':20*math.log10(gain),
            'target_sample_peak_dbfs':-6.0,'premaster_sha256':sha256(premaster)}


def render(drums:Path,v23_unlimited:Path,v23_master:Path,studio_rework:Path, neural_dir:Path,
           workdir:Path, *,kick_db:float=.25, target_lufs:float=-13.7, true_peak:float=-1.40,
           make_ab:bool=True, ffmpeg:str='ffmpeg') -> dict:
    pre=source_preflight(drums,v23_unlimited,v23_master,studio_rework)
    workdir=Path(workdir).resolve()
    if workdir.exists():
        raise FileExistsError('Use a fresh workdir: never overwrite existing experiments')
    neural_dir=Path(neural_dir).resolve()
    for k in MODEL_NAMES:
        if not (neural_dir/(k+'.wav')).is_file():raise FileNotFoundError(f'Actual neural stem missing: {k}.wav')
    if any(workdir==Path(p).resolve() or workdir in Path(p).resolve().parents for p in pre['source_files'].values()):
        raise ValueError('Output location must not overlap source')
    if not shutil.which(ffmpeg):raise RuntimeError('FFmpeg not installed')
    if not (-16.0 <= target_lufs <= -11.0 and -2.0 <= true_peak <= -.8):
        raise ValueError('Unsafe loudness profile for reference experiment')
    # Only publish finished output if ALL stages pass. No automatic overwrite.
    workdir.mkdir(parents=True,exist_ok=False)
    delta_work=workdir/'delta';delta_work.mkdir()
    deltas=build_candidate(drums,v23_unlimited,neural_dir,delta_work,kick_db=kick_db)
    unlimited=delta_work/'neural_kick_candidate_UNMASTERED_float32.wav'
    premaster=workdir/'NEURAL_KICK_PREMASTER_float32.wav'
    norm=normalize_float_premaster(unlimited,premaster)
    q_pre=scan_loudness(premaster,ffmpeg)
    cfg=Config(input=premaster,output=workdir/'Golden_Teeth_Neural_Kick_CANDIDATE_24bit.flac',
               target_lufs=target_lufs,true_peak_ceiling=true_peak,
               lowmid_db=0,presence_db=0,air_db=0,compatible_16bit=True)
    final24=cfg.output
    final16=workdir/'Golden_Teeth_Neural_Kick_CANDIDATE_16bit.flac'
    attempts=[]
    with tempfile.TemporaryDirectory(prefix='neural-v28-',dir=workdir) as t:
        temp=Path(t)
        for i in range(4):
            ceil=true_peak-.15-.15*i
            flo=temp/'post_limiter_float32.wav'
            master_premaster(premaster,flo,cfg,q_pre['input_i'],ceil)
            candidate=temp/'candidate.flac'
            convert_float_to_pcm(flo,candidate,ffmpeg,24)
            q_final=scan_loudness(candidate,ffmpeg)
            attempts.append({'ceiling_setting_dbfs':ceil,'result_truepeak_dbtp':q_final['input_tp']})
            if q_final['input_tp']<=true_peak+.05:
                convert_float_to_pcm(flo,temp/'compatible.flac',ffmpeg,16)
                break
        else:raise RuntimeError('True Peak cannot be satisfied conservatively')
        if sample_count(candidate)!=(pre['frames'],pre['sample_rate'],2) or sample_count(temp/'compatible.flac')!=sample_count(candidate):
            raise RuntimeError('Final frames/grid mismatch')
        if {k:sha256(Path(p)) for k,p in pre['source_files'].items()}!=pre['source_sha256']:
            raise RuntimeError('Source changed during rendering')
        shutil.copyfile(candidate,final24)
        shutil.copyfile(temp/'compatible.flac',final16)
    result={'status':'EXPERIMENTAL_NEURAL_KICK_NOT_LISTENED',
            'real_neural_stems_required':True,'source':pre,'kick_db':kick_db,
            'stem_delta_qc':deltas,'premaster':norm,'premaster_loudnorm':q_pre,
            'master_loudnorm':q_final,'master_ebur128_lufs':independently_scan_ebur128(final24,ffmpeg),
            'master_sha256':sha256(final24),'master16_sha256':sha256(final16),
            'mastering_attempts':attempts,'subjective_qc':'AWAITING_LISTENER',
            'studio_rework_replaced':False, 'v23_master_replaced':False,
            'commercial_use_weights':'NOT_CLEARED'}
    # Comparison only if requested; an A/B is not a blind test.
    if make_ab:
        from make_ab import create_ab
        for reference,tag in [(Path(v23_master),'v23'),(Path(studio_rework),'studio_rework')]:
            ab=workdir/f'Golden_Teeth_{tag}_vs_NeuralKick_AB.flac'
            result[f'ab_{tag}']=create_ab(reference,final24,ab,[42.0,94.0,171.0],seconds=12,ffmpeg=ffmpeg)
    (workdir/'REPORT.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,default=str),encoding='utf8')
    return result


def main():
    a=argparse.ArgumentParser(description=__doc__)
    sub=a.add_subparsers(dest='action',required=True)
    for cmd in ('preflight','render','infer'):
        p=sub.add_parser(cmd)
        p.add_argument('--drums',required=True,type=Path)
        if cmd!='infer':
            p.add_argument('--v23-unlimited',required=True,type=Path)
            p.add_argument('--v23-master',required=True,type=Path)
            p.add_argument('--studio-rework',required=True,type=Path)
        if cmd=='render':
            p.add_argument('--neural-dir',required=True,type=Path)
            p.add_argument('--workdir',required=True,type=Path)
            p.add_argument('--kick-db',type=float,default=.25)
            p.add_argument('--target-lufs',type=float,default=-13.7)
            p.add_argument('--true-peak',type=float,default=-1.40)
            p.add_argument('--skip-ab',action='store_true')
        if cmd=='infer':
            p.add_argument('--output-dir',required=True,type=Path)
            p.add_argument('--cache-dir',required=True,type=Path)
            p.add_argument('--allow-download',action='store_true')
            p.add_argument('--device',default='cpu')
    args=a.parse_args()
    if args.action=='preflight':
        res=source_preflight(args.drums,args.v23_unlimited,args.v23_master,args.studio_rework)
    elif args.action=='infer':
        from drumsep_6stem_float_bridge import run
        res=run(args.drums,args.output_dir,args.cache_dir,device=args.device,allow_download=args.allow_download)
    else:
        res=render(args.drums,args.v23_unlimited,args.v23_master,args.studio_rework,args.neural_dir,args.workdir,
                   kick_db=args.kick_db,target_lufs=args.target_lufs,true_peak=args.true_peak,make_ab=not args.skip_ab)
    print(json.dumps(res,indent=2,ensure_ascii=False,default=str))

if __name__=='__main__':main()