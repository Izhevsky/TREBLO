#!/usr/bin/env python3
"""TREBLO Astra v2.4: safe OPTIONAL neural DrumSep adapter for MSST MDX23C.

Actual neural inference is performed only if the user supplies the official
MSST checkout + exact matching config/checkpoint. No pseudo-stem fallback.
In all modes original input is SHA-256 guarded and never overwritten.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
from dataclasses import dataclass

import numpy as np
import soundfile as sf

STEMS = ('kick', 'snare', 'toms', 'hh', 'cymbals')
ADJUST = {'kick': .32, 'snare': -.28, 'toms': 0., 'hh': .48, 'cymbals': .10}


def sha256(p: Path) -> str:
    with open(p, 'rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()


def safe_path(p: Path) -> Path:
    p=Path(p).expanduser().resolve()
    if not p.is_file(): raise FileNotFoundError(p)
    return p


def model_command(msst_repo: Path, config: Path, checkpoint: Path, input_dir:Path,
                  output_dir:Path, *, cpu:bool=False, python_exe:str=sys.executable) -> list[str]:
    """Uses the real upstream inference.py interface, not a fictional `msst` CLI."""
    entry=safe_path(Path(msst_repo)/'inference.py')
    config=safe_path(config); checkpoint=safe_path(checkpoint)
    if not input_dir.is_dir():raise FileNotFoundError(input_dir)
    if input_dir.resolve()==output_dir.resolve():raise ValueError('input/output directories must differ')
    cmd=[python_exe,str(entry),'--model_type','mdx23c','--config_path',str(config),
         '--start_check_point',str(checkpoint),'--input_folder',str(input_dir),
         '--store_dir',str(output_dir),'--pcm_type','FLOAT',
         '--filename_template','{file_name}/{instr}','--bigshifts','1',
         '--disable_detailed_pbar']
    if cpu:cmd.append('--force_cpu')
    return cmd


def check_model_metadata(config:Path, checkpoint:Path):
    """Only file validity, not model compatibility. Full validation is upstream inference."""
    cfg=safe_path(config); ckpt=safe_path(checkpoint)
    if cfg.suffix.lower() not in ('.yaml','.yml'):raise ValueError('Expected YAML configuration')
    if ckpt.suffix.lower() not in ('.ckpt','.pth','.th'):raise ValueError('Unexpected checkpoint suffix')
    if ckpt.stat().st_size<4096:raise ValueError('Incomplete model weights')
    return {'config_sha256':sha256(cfg),'checkpoint_sha256':sha256(ckpt),'checkpoint_bytes':ckpt.stat().st_size}


def expected_sources(directory:Path, base:str='drums') -> dict[str,Path]:
    """Default upstream output is <output_dir>/<input filename stem>/<instrument>.wav."""
    d=Path(directory)/base
    matches={}
    for name in STEMS:
        p=d/(name+'.wav')
        if not p.is_file():
            raise FileNotFoundError(f'Missing actual MSST neural stem: {p}')
        matches[name]=p
    return matches


def _grid(path):
    with sf.SoundFile(path) as f:
        if f.channels!=2:raise ValueError(f'Stereo required: {path}')
        if f.frames<1000:raise ValueError(f'Audio too short: {path}')
        return (f.frames,f.samplerate)


@dataclass(frozen=True)
class QC:
    max_error_db:float=-15.0
    max_sum_to_source_ratio:float=3.0
    max_delta_db:float=-20.0
    gain_limit_db:float=1.25


def render_delta(drums:Path, model_stems:dict[str,Path], delta_wav:Path,
                 report_path:Path, qc:QC=QC(), changes:dict[str,float]|None=None,
                 block_size:int=65536) -> dict:
    """Gain-deltas from actual neural stems, constrained against source energy.

    Avoids stem double-copy: the ONLY generated audio is sum of (gain-1)*stem.
    The remainder of the original drums stem is NEVER modified.
    Sum-reconstruction error is audited BEFORE complementary residual.
    This QC cannot prove stem purity or audio superiority; ears required.
    """
    drums=safe_path(drums)
    if not isinstance(model_stems,dict) or set(model_stems)!=set(STEMS):
        raise ValueError('All 5 named neural stems are required')
    stems={k:safe_path(v) for k,v in model_stems.items()}
    basegrid=_grid(drums)
    if any(_grid(p)!=basegrid for p in stems.values()):
        raise ValueError('Mismatch in frames/sample-rate: resample/align explicitly before remix')
    gain=dict(ADJUST if changes is None else changes)
    if set(gain)!=set(STEMS) or any(not math.isfinite(v) or abs(v)>qc.gain_limit_db for v in gain.values()):
        raise ValueError('Unsafe or missing gain')
    if delta_wav.resolve()==drums.resolve() or delta_wav.resolve() in [p.resolve() for p in stems.values()]:
        raise ValueError('Output must not overwrite any input')
    sha0={"drums":sha256(drums),**{k:sha256(v) for k,v in stems.items()}}
    e0=ed=esum=eres=0.;peakdiff=0.;frames=0
    if delta_wav.exists():raise FileExistsError(f'Output already exists: {delta_wav}')
    delta_wav.parent.mkdir(parents=True,exist_ok=True)
    with sf.SoundFile(drums) as original:
        with __import__('contextlib').ExitStack() as stack:
            fs={k:stack.enter_context(sf.SoundFile(v)) for k,v in stems.items()}
            # Write to staging until checks pass. Never deliver a misleading result.
            staging=delta_wav.with_name(delta_wav.name+'.partial.wav')
            try:
                with sf.SoundFile(staging,'w',samplerate=basegrid[1],channels=2,subtype='FLOAT') as target:
                    while True:
                        a=original.read(block_size,dtype='float64',always_2d=True)
                        if len(a)==0:break
                        parts={k:f.read(len(a),dtype='float64',always_2d=True) for k,f in fs.items()}
                        if not np.isfinite(a).all() or any(not np.isfinite(p).all() for p in parts.values()):
                            raise ValueError('NaN/Inf in audio')
                        mixed=sum(parts.values())
                        delta=sum((10**(gain[k]/20)-1)*parts[k] for k in STEMS)
                        err=a-mixed
                        e0+=float(np.sum(a*a));ed+=float(np.sum(delta*delta))
                        esum+=float(np.sum(mixed*mixed));eres+=float(np.sum(err*err))
                        peakdiff=max(peakdiff,float(np.max(abs(delta))))
                        frames+=len(a)
                        target.write(delta.astype('float32'))
                err_db=10*math.log10((eres+1e-30)/(e0+1e-30))
                delta_db=10*math.log10((ed+1e-30)/(e0+1e-30))
                sum_ratio=math.sqrt(esum/max(e0,1e-30))
                status=('PASS' if err_db<=qc.max_error_db and
                        delta_db<=qc.max_delta_db and sum_ratio<=qc.max_sum_to_source_ratio else 'REVIEW')
                result={'engine':'neural_msst_mdx23c_not_dsp_proxies',
                        'input_sha256':sha0,'frames':frames,'sample_rate':basegrid[1],
                        'sum_reconstruction_error_db':err_db,'delta_relative_rms_db':delta_db,
                        'predicted_sum_to_source_rms':sum_ratio,
                        'max_abs_delta':peakdiff,'gain_db':gain,'qc_status':status,
                        'automatic_master_approved':False,
                        'notes':'No claims of perfect isolation; residual untouched. Manual listening required.'}
                if status!='PASS':
                    staging.unlink(missing_ok=True)
                    report_path.parent.mkdir(parents=True,exist_ok=True)
                    report_path.write_text(json.dumps(result,ensure_ascii=False,indent=2))
                    raise RuntimeError(f'DrumSep QC rejected result: err {err_db:.2f} dB; delta {delta_db:.2f} dB; sum/source {sum_ratio:.3f}')
                if {k:sha256(p) for k,p in [('drums',drums),*stems.items()]}!=sha0:
                    raise RuntimeError('Input modified during processing')
                staging.replace(delta_wav)
            finally:
                staging.unlink(missing_ok=True)
    result['delta_sha256']=sha256(delta_wav)
    report_path.parent.mkdir(parents=True,exist_ok=True)
    report_path.write_text(json.dumps(result,ensure_ascii=False,indent=2))
    return result


def apply_delta(baseline_unlimited:Path,delta:Path,output:Path, *, max_difference_db=-20.0):
    """Intermediate float32 mix only, NOT a mastered FLAC. Keep old master unchanged."""
    baseline_unlimited=safe_path(baseline_unlimited);delta=safe_path(delta)
    if _grid(baseline_unlimited)!=_grid(delta):raise ValueError('Mix/delta grid mismatch')
    if output.resolve() in (baseline_unlimited.resolve(),delta.resolve()):raise ValueError('Overwrite forbidden')
    if output.exists():raise FileExistsError(f'Output already exists: {output}')
    s0=sha256(baseline_unlimited);s1=sha256(delta)
    output.parent.mkdir(parents=True,exist_ok=True)
    stage=output.with_name(output.name+'.partial.wav');outenergy=diffenergy=0.
    try:
        with sf.SoundFile(baseline_unlimited) as base, sf.SoundFile(delta) as d:
            with sf.SoundFile(stage,'w',samplerate=base.samplerate,channels=2,subtype='FLOAT') as o:
                while True:
                    a=base.read(65536,dtype='float64',always_2d=True)
                    if not len(a):break
                    z=d.read(len(a),dtype='float64',always_2d=True)
                    if not np.isfinite(a).all() or not np.isfinite(z).all():raise ValueError('Nonfinite source')
                    outenergy+=float(np.sum(a*a));diffenergy+=float(np.sum(z*z))
                    o.write((a+z).astype('float32'))
        relative_db=10*math.log10((diffenergy+1e-30)/(outenergy+1e-30))
        if relative_db>max_difference_db:raise RuntimeError('Delta unexpectedly large')
        if sha256(baseline_unlimited)!=s0 or sha256(delta)!=s1:raise RuntimeError('Input modified')
        stage.replace(output)
        return {'relative_delta_db':relative_db,'output_sha256':sha256(output),'not_mastered':True}
    finally:stage.unlink(missing_ok=True)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    sub=ap.add_subparsers(dest='action',required=True)
    se=sub.add_parser('inference')
    for k in ('msst_repo','config','checkpoint','input_dir','output_dir'):
        se.add_argument('--'+k.replace('_','-'),type=Path,required=True)
    se.add_argument('--cpu',action='store_true');se.add_argument('--dry-run',action='store_true')
    d=sub.add_parser('delta')
    d.add_argument('--drums',type=Path,required=True)
    d.add_argument('--predicted-dir',type=Path,required=True)
    d.add_argument('--file-stem',default='drums')
    d.add_argument('--output',type=Path,required=True);d.add_argument('--report',type=Path,required=True)
    m=sub.add_parser('mix')
    m.add_argument('--baseline-unlimited',type=Path,required=True)
    m.add_argument('--delta',type=Path,required=True);m.add_argument('--output',type=Path,required=True)
    a=ap.parse_args()
    if a.action=='inference':
        check_model_metadata(a.config,a.checkpoint)
        cmd=model_command(a.msst_repo,a.config,a.checkpoint,a.input_dir,a.output_dir,cpu=a.cpu)
        if a.dry_run:print(json.dumps({'status':'READY_NOT_RUN','cmd':cmd},indent=2));return
        a.output_dir.mkdir(parents=True,exist_ok=True)
        subprocess.run(cmd,check=True,timeout=10800)
        return
    if a.action=='delta':
        q=render_delta(a.drums,expected_sources(a.predicted_dir,a.file_stem),a.output,a.report)
        print(json.dumps(q,indent=2));return
    print(json.dumps(apply_delta(a.baseline_unlimited,a.delta,a.output),indent=2))

if __name__=='__main__':main()