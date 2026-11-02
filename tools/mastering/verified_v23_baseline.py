#!/usr/bin/env python3
"""TREBLO v2.9: rebuild & prove Golden Teeth v2.3's unmastered source.

Requires locally held ORIGINAL audio, six original stems and the approved v2.3
master. No remote uploads, no neural inference, no invented audio source.
Rebuilds with the original v2.3 chain, then fails closed if the rebuilt master
is not BIT IDENTICAL in decoded 24-bit PCM to the approved reference.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import soundfile as sf
import numpy as np

STEM_NAMES = ('drums','bass','other','piano','guitar','vocals')
R = 'rebuilt_reference_v23.flac'
RAW = 'raw_v23_float.wav'
PRE = 'PREMASTER_float32.wav'


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for buf in iter(lambda:f.read(4*1024*1024),b''):
            h.update(buf)
    return h.hexdigest()


def pcm_comparison(a:Path,b:Path,frames=131072)->dict:
    a,b=Path(a),Path(b)
    if not a.is_file() or not b.is_file():raise FileNotFoundError('Both masters required')
    with sf.SoundFile(a) as x,sf.SoundFile(b) as y:
        g1=(x.frames,x.samplerate,x.channels,x.subtype)
        g2=(y.frames,y.samplerate,y.channels,y.subtype)
        if g1!=g2:raise ValueError(f'Incompatible grids or PCM subtype: {g1} vs {g2}')
        if x.subtype !='PCM_24':raise ValueError('Master must be 24-bit PCM FLAC')
        mismatches=0;max_diff=0.0;energy=0.0;cross=0.0;pa=0.0;pb=0.0
        while 1:
            p=x.read(frames,dtype='float64',always_2d=True)
            q=y.read(frames,dtype='float64',always_2d=True)
            if not len(p):break
            if not np.isfinite(p).all() or not np.isfinite(q).all():raise ValueError('Non-finite audio')
            mismatches+=int(np.count_nonzero(p!=q))
            diff=p-q;max_diff=max(max_diff,float(np.max(np.abs(diff))))
            energy+=float(np.sum(diff*diff));cross+=float(np.sum(p*q))
            pa+=float(np.sum(p*p));pb+=float(np.sum(q*q))
        return {'frames':g1[0],'sample_rate':g1[1],'channels':g1[2],
                'subtype':g1[3],'mismatched_channel_samples':mismatches,
                'max_absolute_difference':max_diff,
                'relative_error_db':None if energy==0 else float(10*np.log10(energy/max(pb,1e-40))),
                'correlation':float(cross/np.sqrt(pa*pb)) if pa>0 and pb>0 else None,
                'decoded_pcm_exact':mismatches==0}


def verify(original:Path,stem_dir:Path,reference:Path,workdir:Path,*,emit=True)->dict:
    original=Path(original).resolve();stem_dir=Path(stem_dir).resolve()
    reference=Path(reference).resolve();workdir=Path(workdir).resolve()
    if not original.is_file() or not reference.is_file():raise FileNotFoundError('Original/reference absent')
    stems={name:stem_dir/f'{name} golden teeth.wav' for name in STEM_NAMES}
    for name,p in stems.items():
        if not p.is_file():raise FileNotFoundError(f'Stem missing: {name}: {p}')
    files={'original':original,**stems}
    manifest=workdir/'source_manifest_v23.json'
    if not manifest.is_file():raise FileNotFoundError('Run build stage; source SHA manifest missing')
    registered=json.loads(manifest.read_text())
    checked={name:sha256(p) for name,p in files.items()}
    if registered!=checked:raise RuntimeError('Source SHA-256 changed: stop!')
    raw=workdir/RAW;pre=workdir/PRE;rebuilt=workdir/R
    for p in [raw,pre,rebuilt]:
        if not p.is_file():raise FileNotFoundError(f'Missing stage: {p}')
    with sf.SoundFile(raw) as f:
        g=(f.frames,f.samplerate,f.channels)
        if f.subtype!='FLOAT':raise ValueError('Unlimited input is not float32 WAV')
    with sf.SoundFile(pre) as f:
        if f.subtype!='FLOAT' or g!=(f.frames,f.samplerate,f.channels):
            raise ValueError('Premaster mismatch or not float32')
    comp=pcm_comparison(rebuilt,reference)
    if tuple(comp[k] for k in ('frames','sample_rate','channels'))!=g:
        raise ValueError('Master differs in length/rate/channels')
    file_hash_matches=sha256(rebuilt)==sha256(reference)
    out={'version':'TREBLO_v2.9_exact_v23_source_recovery',
         'build_status':'PASS' if comp['decoded_pcm_exact'] and file_hash_matches else 'FAIL',
         'reference_file_sha256':sha256(reference),'rebuilt_file_sha256':sha256(rebuilt),
         'file_container_exact':file_hash_matches,'reference_pcm':comp,
         'source_files_sha256':checked,'unlimited_float32':{'filename':raw.name,'sha256':sha256(raw)},
         'premaster_float32':{'filename':pre.name,'sha256':sha256(pre)},
         'neural_model_executed':False,'original_and_masters_modified':False,
         'candidate_status':'READY_FOR_LOCAL_NEURAL_STEM_INFERENCE_NOT_MASTERED',
         'approved_studio_rework_overwritten':False}
    if emit:
        (workdir/'VERIFIED_V23_LINEAGE.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
    if out['build_status']!='PASS':raise RuntimeError('Rebuilt master not identical; DO NOT use raw candidate')
    return out


def build(original:Path,stem_dir:Path,reference:Path,workdir:Path)->dict:
    workdir=Path(workdir).resolve()
    original=Path(original).resolve();reference=Path(reference).resolve()
    if workdir.exists():raise FileExistsError('Build requires NEW empty directory; refuse overwrite')
    if workdir==original.parent or workdir==reference.parent:raise ValueError('No writing into source directory')
    from render_v23_resumable import run
    output=workdir/R
    for stage in ('prepare','mix','master'):
        run(original,Path(stem_dir),workdir,output,stage,False)
    return verify(original,stem_dir,reference,workdir)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['build','verify'])
    p.add_argument('--original',type=Path,required=True)
    p.add_argument('--stems-dir',type=Path,required=True)
    p.add_argument('--reference-v23',type=Path,required=True)
    p.add_argument('--workdir',type=Path,required=True)
    a=p.parse_args()
    args=(a.original,a.stems_dir,a.reference_v23,a.workdir)
    result=build(*args) if a.action=='build' else verify(*args)
    print(json.dumps({'status':result['build_status'],
          'sha256_equal':result['file_container_exact'],
          'pcm_samples_mismatched':result['reference_pcm']['mismatched_channel_samples'],
          'unlimited':str(Path(a.workdir)/RAW)},indent=2))

if __name__=='__main__':main()