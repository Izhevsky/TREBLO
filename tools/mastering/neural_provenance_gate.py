#!/usr/bin/env python3
"""TREBLO v3.0: integrity/provenance gate for DrumSep v2.5 neural outputs.

Provenance records are SELF-REPORTED by the inference adapter, not cryptographic
proof of the model architecture. Treat as data-integrity QC, not attestation.
Does not process audio, import PyTorch, download checkpoints, or publish stems.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from contextlib import ExitStack
from pathlib import Path
import soundfile as sf
import numpy as np

EXPECTED_WEIGHTS = 'd2a4aa53eb584d21eead358a4e66d1882ad182911be018f052b5da73be9096d0'
EXPECTED_CONFIG = '17d1649a227f841165bdb4c11a42082898192a1ea3ceab7e7e0b9293d6589dd6'
STEMS = ('kick','snare','toms','hh','cymbals')

def digest(path:Path) -> str:
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()

def info(path:Path):
    with sf.SoundFile(path) as a:
        return (a.frames,a.samplerate,a.channels,a.subtype)

def _zero_lag_ratio(source:np.ndarray, stems_sum:np.ndarray, margin:int=12) -> int:
    """Highest center-correlation lag (within +-margin) for one window.
    Use absolute correlation to avoid polarity mistakes; phase changes are
    separately captured by the reconstruction error metric.
    """
    x=np.mean(source,axis=1); y=np.mean(stems_sum,axis=1)
    if np.dot(x,x)<1.e-10 or np.dot(y,y)<1.e-10:return 0
    bestlag=0;best=-1
    for lag in range(-margin,margin+1):
        xx=x[max(0,lag):len(x)+min(0,lag)]
        yy=y[max(0,-lag):len(y)+min(0,-lag)]
        prod=float(np.dot(xx,yy))
        v=abs(prod)/math.sqrt(float(np.dot(xx,xx)*np.dot(yy,yy))+1e-30)
        if v>best:best=v;bestlag=lag
    return bestlag

def check(drums:Path, predicted:Path, *, max_reconstruction_db=-15., window_seconds=5., max_window_error_db=-10., max_lag=1, block_size=44100*5)->dict:
    drums=Path(drums).resolve();predicted=Path(predicted).resolve()
    report=predicted/'INFERENCE_REPORT.json'
    if not drums.is_file():raise FileNotFoundError(drums)
    if not report.is_file():raise FileNotFoundError('Missing original INFERENCE_REPORT.json from real inference')
    j=json.loads(report.read_text(encoding='utf-8'))
    if j.get('inference_performed') is not True or j.get('engine')!='mdxnet_infer_mdx23c_6stem' or j.get('model')!='drumsep-6stem':
        raise ValueError('Neural inference provenance missing or wrong; synthetic substitutes forbidden')
    if j.get('weights_expected_sha256')!=EXPECTED_WEIGHTS or j.get('model_config_expected_sha256')!=EXPECTED_CONFIG:
        raise ValueError('Unexpected checkpoint/config identity')
    if j.get('output_type')!='actual_neural_predictions_float32_WAV' or set(j.get('output_stems',[]))!=set(STEMS):
        raise ValueError('Wrong stem format or labels')
    if not isinstance(j.get('stems_sha256'),dict) or set(j['stems_sha256'])!=set(STEMS):
        raise ValueError('Incomplete stem hash registry')
    src_sha=digest(drums)
    if j.get('source_sha256')!=src_sha:raise ValueError('Neural predictions belong to a different drums file')
    shape=info(drums)
    if shape[1:]!=(44100,2,'PCM_16') and (shape[1]!=44100 or shape[2]!=2):
        raise ValueError('Source grid incompatible')
    if j.get('frames')!=shape[0] or j.get('sample_rate')!=shape[1] or j.get('channels')!=shape[2]:
        raise ValueError('Report grid contradicts source')
    paths={name:predicted/(name+'.wav') for name in STEMS}
    for name,p in paths.items():
        if not p.is_file():raise FileNotFoundError(p)
        if p.resolve()==drums:raise ValueError('Output stem equals source')
        if info(p)!=(shape[0],shape[1],shape[2],'FLOAT'):
            raise ValueError(f'{name}: require exact float32 grid')
        if digest(p)!=j['stems_sha256'][name]:raise ValueError(f'{name}: SHA-256 mismatch')
    recon=source_power=0.
    windows=[]; offsets=[]
    with ExitStack() as stack:
        ref=stack.enter_context(sf.SoundFile(drums))
        sep={k:stack.enter_context(sf.SoundFile(p)) for k,p in paths.items()}
        pos=0
        while pos<shape[0]:
            n=min(int(window_seconds*shape[1]),shape[0]-pos)
            x=ref.read(n,dtype='float64',always_2d=True)
            y=sum((f.read(n,dtype='float64',always_2d=True) for f in sep.values()),np.zeros_like(x))
            if not (np.isfinite(x).all() and np.isfinite(y).all()):raise ValueError('NaN or Inf in audio')
            se=float(np.sum(x*x));de=float(np.sum((x-y)**2))
            ratio=10*math.log10((de+1.e-30)/(se+1.e-30))
            lag=_zero_lag_ratio(x,y) if n>=2048 else 0
            windows.append({'start_seconds':round(pos/shape[1],4),'error_db':round(ratio,3),'lag_samples':lag})
            offsets.append(lag)
            recon+=de;source_power+=se;pos+=n
    total=10*math.log10((recon+1.e-30)/(source_power+1.e-30))
    if total > max_reconstruction_db:raise ValueError(f'Reconstruction QC failed: {total:.2f} dB > {max_reconstruction_db} dB')
    # Very quiet tail windows can create meaningless dB errors; use only windows with
    # sufficient reference energy for hard local gate.
    active_w=[w for w in windows if w['error_db']<20.]
    if active_w and max(w['error_db'] for w in active_w)>max_window_error_db:
        raise ValueError('Local reconstruction QC failed')
    if any(abs(lag)>max_lag for lag in offsets):raise ValueError('Neural stems misaligned to drums source')
    return {'status':'NEURAL_INPUTS_CHECKED_NOT_PERCEPTUALLY_APPROVED',
        'model':j['model'],'actual_inference_claimed_in_report':True,
        'cryptographic_model_execution_attestation':False,
        'drums_sha256':src_sha,'stems_sha256':j['stems_sha256'],
        'source_frames':shape[0],'rate':shape[1],
        'reconstruction_error_db':round(total,4),'max_window_error_db':max(w['error_db'] for w in windows),
        'max_abs_lag_samples':max(abs(z) for z in offsets), 'windows':windows,
        'next_step':'Kick-only delta candidate limited to <= 0.35 dB; listening test required'}

def doctor(drums:Path, premaster:Path, model_cache:Path)->dict:
    drums=Path(drums);premaster=Path(premaster);model_cache=Path(model_cache)
    r={'drums_present':drums.is_file(),'unlimited_float_present':premaster.is_file(),'cache_path':str(model_cache),
       'checkpoint_expected_sha256':EXPECTED_WEIGHTS,'config_expected_sha256':EXPECTED_CONFIG}
    if drums.is_file():r.update(drums_sha256=digest(drums),drums_grid=info(drums))
    if premaster.is_file():r.update(unlimited_sha256=digest(premaster),unlimited_grid=info(premaster))
    r['checkpoint_present']=any(p.is_file() and 'drumsep' in p.name.lower() and p.suffix=='.ckpt' for p in model_cache.rglob('*.ckpt')) if model_cache.exists() else False
    r['can_run_real_neural_inference_locally']=r['checkpoint_present'] and r['drums_present'] and r['unlimited_float_present']
    return r

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['doctor','check']);ap.add_argument('--drums',type=Path,required=True);ap.add_argument('--unlimited',type=Path);ap.add_argument('--predicted',type=Path);ap.add_argument('--cache',type=Path,default=Path.home()/'.cache/mdxnet-infer');ap.add_argument('--output',type=Path)
    a=ap.parse_args()
    r=doctor(a.drums,a.unlimited,a.cache) if a.mode=='doctor' else check(a.drums,a.predicted)
    print(json.dumps(r,ensure_ascii=False,indent=2))
    if a.output:a.output.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')