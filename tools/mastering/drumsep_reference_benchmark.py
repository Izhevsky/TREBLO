#!/usr/bin/env python3
"""TREBLO v2.7 — evaluate REAL DrumSep against synthetic stems with known sources.

SYNTHETIC ORIGINAL drum audio only. No user audio is sent to GitHub Actions.
The quality metrics are exploratory: synthetic sources are not distribution-matched
with recorded/AI-generated percussion and do not prove quality on Golden Teeth.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
from typing import Mapping
import numpy as np
from scipy.signal import butter, sosfilt

LABELS = ('kick','snare','toms','hh','ride','crash')
SR = 44100


def make_reference(*, seconds: float = 7.0, seed: int = 20261101):
    """Generate deterministic ORIGINAL (not sampled) percussive audio.

    All six independent ground-truth stems have identical sample grids.
    """
    if not 2 <= seconds <= 15: raise ValueError('2..15 seconds required')
    rng=np.random.default_rng(seed)
    n=round(seconds*SR)
    stems={k:np.zeros((n,2),dtype=np.float64) for k in LABELS}
    beat=60/122

    def put(label,onset,mono,left=.99,right=.99):
        i=int(round(onset*SR))
        if i>=n or i<0:return
        seg=mono[:n-i]
        stems[label][i:i+len(seg),0]+=left*seg
        stems[label][i:i+len(seg),1]+=right*seg

    for i,at in enumerate(np.arange(.15,seconds-.03,beat)):
        t=np.arange(int(.27*SR))/SR
        freq=52+74*np.exp(-t*38)
        phase=2*np.pi*np.cumsum(freq)/SR
        kick=.29*np.sin(phase)*np.exp(-t*19)*(1-np.exp(-t*1200))
        put('kick',at,kick,.99,1.00)
        if i%2==1:
            t=np.arange(int(.20*SR))/SR
            noise=rng.normal(size=len(t))
            noise=sosfilt(butter(3,[420,8900],fs=SR,output='sos',btype='band'),noise)
            sig=.085*noise*np.exp(-t*23)+.032*np.sin(2*np.pi*175*t)*np.exp(-t*32)
            put('snare',at,sig,1.,.97)
        if i%4==2:
            t=np.arange(int(.26*SR))/SR
            freq=152+95*np.exp(-t*13)
            sig=.075*np.sin(2*np.pi*np.cumsum(freq)/SR)*np.exp(-t*16)
            put('toms',at+.095,sig,.98,1.)
    for i,at in enumerate(np.arange(.15,seconds-.03,beat/2)):
        t=np.arange(int(.075*SR))/SR
        x=sosfilt(butter(3,6500,fs=SR,btype='high',output='sos'),rng.normal(size=len(t)))
        sig=.055*x*np.exp(-t*65)
        put('hh',at,sig,.93,1.)
    for i,at in enumerate(np.arange(.15+beat*.5,seconds-.1,beat*2)):
        t=np.arange(int(.42*SR))/SR
        x=sosfilt(butter(3,3600,fs=SR,btype='high',output='sos'),rng.normal(size=len(t)))
        sig=.028*x*np.exp(-t*11)+.008*np.sin(2*np.pi*6400*t)*np.exp(-t*19)
        put('ride',at,sig,1.,.85)
    for at in np.arange(.15+beat*4,seconds-.1,beat*8):
        t=np.arange(int(1.08*SR))/SR
        x=sosfilt(butter(3,2200,fs=SR,btype='high',output='sos'),rng.normal(size=len(t)))
        sig=.035*x*np.exp(-t*3.8)
        put('crash',at,sig,.83,1.)
    mixture=sum(stems.values(),np.zeros((n,2),dtype=np.float64))
    peak=float(np.max(abs(mixture)))
    if peak>0.79:
        factor=.79/peak
        mixture*=factor
        for k in stems:stems[k]*=factor
    return {k:v.astype('float32') for k,v in stems.items()}, mixture.astype('float32')


def score_sources(reference:Mapping[str,np.ndarray],out:Mapping[str,np.ndarray],mixture:np.ndarray)->dict:
    if set(reference)!=set(LABELS) or set(out)!=set(LABELS):
        raise ValueError('Six expected stems required')
    if mixture.ndim!=2 or mixture.shape[1]!=2 or not np.isfinite(mixture).all():
        raise ValueError('Bad input mixture')
    src={k:np.asarray(reference[k],dtype='float64') for k in LABELS}
    dst={k:np.asarray(out[k],dtype='float64') for k in LABELS}
    for k in LABELS:
        if src[k].shape!=mixture.shape or dst[k].shape!=mixture.shape:
            raise ValueError('Bad output grid '+k)
        if not np.isfinite(src[k]).all() or not np.isfinite(dst[k]).all():
            raise ValueError('Non-finite source or output')
    pred=sum(dst.values(),np.zeros_like(mixture,dtype='float64'))
    mix=np.asarray(mixture,dtype='float64')
    recon=10*np.log10((np.sum((mix-pred)**2)+1e-30)/(np.sum(mix**2)+1e-30))
    # source is sparse; report per-source projection SI-SDR plus leakage proxies.
    details={}
    for k in LABELS:
        s=src[k].ravel();p=dst[k].ravel()
        scale=float(np.dot(s,p)/(np.dot(s,s)+1e-30))
        projected=scale*s
        e=p-projected
        si_sdr=float(10*np.log10((np.dot(projected,projected)+1e-30)/(np.dot(e,e)+1e-30)))
        dot=float(np.dot(s,p));co=float(dot/(np.linalg.norm(s)*np.linalg.norm(p)+1e-30))
        details[k]={
           'source_rms':float(np.sqrt(np.mean(s*s))),
           'model_rms':float(np.sqrt(np.mean(p*p))),
           'si_sdr_db':round(si_sdr,3),
           'cosine_similarity':round(co,6),
           'gain_to_reference_db':round(20*np.log10(np.sqrt(np.mean(p*p))+1e-15)-20*np.log10(np.sqrt(np.mean(s*s))+1e-15),3),
        }
    return {'status':'SIX_STEM_MODEL_OUTPUT_EVALUATED','frames':int(mixture.shape[0]),'sample_rate':SR,
            'sum_reconstruction_error_db':round(float(recon),4),
            'measurements':details,'perceptual_quality_approved':False,
            'real_music_generalization':'NOT_TESTED',
            'warning':'High SDR on a synthetic fixture does not imply isolation quality on Golden Teeth.'}


def benchmark_real(*, seconds=7.0,cache_dir=None,allow_download=False,device='cpu',output=None):
    # Import bridge only at run time: keeps unit tests totally offline.
    from drumsep_6stem_float_bridge import require_registry, MODEL, CHECKPOINT_SHA256, CONFIG_SHA256
    from mdxnet_infer import MDX23CInference
    cache=Path(cache_dir or Path.home()/'.cache'/'mdxnet-infer').expanduser()
    require_registry(cache,allow_download)
    refs,mixture=make_reference(seconds=seconds)
    model=MDX23CInference.from_pretrained(MODEL,device=device,cache_dir=cache,progress=False)
    pred=model.separate(mixture,sample_rate=SR,progress=False)
    qc=score_sources(refs,pred,mixture)
    qc['model']='mdxnet-infer/drumsep-6stem';qc['checkpoint_sha256']=CHECKPOINT_SHA256
    qc['config_sha256']=CONFIG_SHA256;qc['inputs']='synthetic_non_user_original_drums'
    if output:
        p=Path(output);p.parent.mkdir(parents=True,exist_ok=True)
        if p.exists():raise FileExistsError(p)
        p.write_text(json.dumps(qc,ensure_ascii=False,indent=2),encoding='utf-8')
    return qc


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--seconds',type=float,default=7.0)
    p.add_argument('--device',choices=['cpu','cuda'],default='cpu')
    p.add_argument('--cache-dir',type=Path)
    p.add_argument('--allow-download',action='store_true')
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(benchmark_real(seconds=a.seconds,cache_dir=a.cache_dir,
                allow_download=a.allow_download,device=a.device,output=a.output),indent=2))
if __name__=='__main__':main()