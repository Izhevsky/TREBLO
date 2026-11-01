#!/usr/bin/env python3
"""TREBLO Astra v2.5: real MDX23C DrumSep 6-stem inference -> lossless-ish float32 staging.

No music synthesis, no spectral pseudo stems, no mastering, no upload of input.
Model checksum is validated by mdxnet-infer. Downloads require explicit approval.
Audio source is immutable and must already be stereo at 44.1 kHz.
No automatic gain changes: output is ONLY neural stem predictions.
License of third-party checkpoint needs separate clearance for commercial use.
"""
from __future__ import annotations
import argparse
from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
import tempfile
from typing import Any

import numpy as np
import soundfile as sf

MODEL = 'drumsep-6stem'
SIX = ('kick','snare','toms','hh','ride','crash')
FIVE = ('kick','snare','toms','hh','cymbals')
CHECKPOINT_SHA256 = 'd2a4aa53eb584d21eead358a4e66d1882ad182911be018f052b5da73be9096d0'
CONFIG_SHA256 = '17d1649a227f841165bdb4c11a42082898192a1ea3ceab7e7e0b9293d6589dd6'


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024), b''):h.update(block)
    return h.hexdigest()


def inspect_source(path: Path) -> dict[str,Any]:
    path=Path(path).resolve()
    if not path.is_file():raise FileNotFoundError(path)
    with sf.SoundFile(path) as f:
        if f.channels!=2 or f.samplerate!=44100 or f.frames<1024:
            raise ValueError('DrumSep v2.5 requires existing 44.1 kHz stereo drums WAV (no implicit resampling)')
        info={'file':str(path),'sample_rate':f.samplerate,'frames':f.frames,'channels':f.channels,
              'source_subtype':f.subtype,'duration_sec':round(f.frames/f.samplerate,6), 'source_sha256':sha256(path)}
    return info


def require_registry(cache: Path, allow_download: bool) -> None:
    """Fail offline by default, never unknowingly reach out to download model."""
    try:
        from mdxnet_infer.checkpoint_catalog import get_checkpoint_metadata
    except ImportError as e:
        raise RuntimeError('Install mdxnet-infer from pinned, reviewed GitHub revision first') from e
    meta=get_checkpoint_metadata(MODEL)
    if not meta or meta['checkpoint_sha256']!=CHECKPOINT_SHA256 or meta['config_sha256']!=CONFIG_SHA256:
        raise RuntimeError('Model registry checksum mismatch; refusing unreviewed change')
    if not allow_download:
        needed={a['kind']:a for a in meta['artifacts']}
        for kind in ('checkpoint','config'):
            p=cache/needed[kind]['name']
            if not p.is_file():raise FileNotFoundError(f'Model cache empty: {p}; explicitly choose --allow-download to fetch public weights')
            if sha256(p)!=needed[kind]['sha256']:
                raise RuntimeError(f'{kind} checksum mismatch: {p}')


def run(input_path: Path, output_dir: Path, cache_dir: Path, *, device:str='cpu',
        allow_download:bool=False, dry_run:bool=False, engine_factory=None) -> dict:
    input_path=Path(input_path).resolve();output_dir=Path(output_dir).resolve();cache_dir=Path(cache_dir).expanduser().resolve()
    preflight=inspect_source(input_path)
    if output_dir==input_path.parent or output_dir==input_path or output_dir in input_path.parents:
        raise ValueError('Use a separate destination, never the source directory')
    target=output_dir/input_path.stem
    if target.exists():raise FileExistsError(f'Refusing overwrite of existing stem directory: {target}')
    if device!='cpu' and device!='cuda' and not (device.startswith('cuda:') and device[5:].isdigit()):
        raise ValueError('Expected cpu/cuda/cuda:N')
    if dry_run:
        return {**preflight,'status':'DRY_RUN_NOT_INFERRED','model':MODEL,'target':str(target),
                'cache':str(cache_dir),'allow_download':allow_download,'inference_performed':False}
    if engine_factory is None:
        require_registry(cache_dir,allow_download)
        from mdxnet_infer import MDX23CInference
        engine_factory=lambda:MDX23CInference.from_pretrained(MODEL,device=device,cache_dir=cache_dir,progress=True)
    src, sr=sf.read(input_path,dtype='float32',always_2d=True)
    if not np.isfinite(src).all():raise ValueError('Nonfinite source audio')
    model=engine_factory()
    output=model.separate(src,sample_rate=sr,progress=False)
    if set(output)!=set(SIX):raise ValueError(f'Unexpected neural instrument labels: {list(output)}')
    decoded={k:np.asarray(output[k],dtype=np.float32) for k in SIX}
    if any(a.shape!=src.shape or not np.isfinite(a).all() for a in decoded.values()):
        raise ValueError('Neural output nonfinite, wrong number of channels or wrong frames')
    # Combine float32 before writing; the standard CLI silently quantizes each stem to PCM16.
    decoded['cymbals']=(decoded['ride'].astype('float64')+decoded['crash'].astype('float64')).astype('float32')
    prediction=sum((decoded[k].astype('float64') for k in FIVE),np.zeros_like(src,dtype='float64'))
    reconstruction_error_db=10*np.log10((np.sum((src.astype('float64')-prediction)**2)+1e-25)/(np.sum(src.astype('float64')**2)+1e-25))
    # Only stage outputs in a fresh temp directory. Even bad sums may be useful for listening, not auto-approved.
    output_dir.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='drumsep-v25-',dir=output_dir) as temp:
        staging=Path(temp)/input_path.stem
        staging.mkdir()
        for stem in FIVE:
            sf.write(staging/(stem+'.wav'), decoded[stem], sr, subtype='FLOAT')
        manifests={stem:sha256(staging/(stem+'.wav')) for stem in FIVE}
        report={**preflight,'model':MODEL,'inference_performed':True,'engine':'mdxnet_infer_mdx23c_6stem',
                'output_type':'actual_neural_predictions_float32_WAV','output_stems':list(FIVE),
                'prediction_reconstruction_error_db':round(float(reconstruction_error_db),3),
                'stems_sha256':manifests,
                'weights_expected_sha256':CHECKPOINT_SHA256,'model_config_expected_sha256':CONFIG_SHA256,
                'automatic_master_approved':False,
                'evaluation':'Predictions may bleed and reconstruction error is not a measure of purity',
                'third_party_weights_license':'Not formally documented by original authors: noncommercial/permission review required'}
        (staging/'INFERENCE_REPORT.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
        if sha256(input_path)!=preflight['source_sha256']:raise RuntimeError('Source modified during inference')
        staging.rename(target)
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',required=True,type=Path)
    parser.add_argument('--output-dir',required=True,type=Path)
    parser.add_argument('--cache-dir',type=Path,default=Path.home()/'.cache'/'mdxnet-infer')
    parser.add_argument('--device',default='cpu')
    parser.add_argument('--allow-download',action='store_true',help='Explicit consent to download public model weights; never uploads audio')
    parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args()
    result=run(args.input,args.output_dir,args.cache_dir,device=args.device,allow_download=args.allow_download,dry_run=args.dry_run)
    print(json.dumps(result,indent=2,ensure_ascii=False))

if __name__=='__main__':main()