#!/usr/bin/env python3
"""MSST optional external stem separation. Never assumes a checkpoint/model exists."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import soundfile as sf


def sha256(path: Path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def separation_command(*, model_type: str, config: Path, checkpoint: Path,
                       input_folder: Path, output_folder: Path, device_ids: int = 0,
                       force_cpu: bool = False) -> list[str]:
    for f in [config, checkpoint]:
        if not f.is_file():
            raise FileNotFoundError(f'MSST requires existing model configuration and weights: {f}')
    if not input_folder.is_dir():
        raise FileNotFoundError(input_folder)
    if input_folder.resolve() == output_folder.resolve():
        raise ValueError('Input and output folders must differ')
    cmd = ['msst', 'inference', '--model_type', model_type,
           '--config_path', str(config), '--start_check_point', str(checkpoint),
           '--input_folder', str(input_folder), '--store_dir', str(output_folder),
           '--device_ids', str(device_ids)]
    if force_cpu:
        cmd += ['--force_cpu']
    return cmd


def validate_reconstruction(mix: Path, stems: list[Path], max_error_db: float = -25.0) -> dict:
    """Diagnostic only. Neural output must never silently replace the source.

    All files must have the same sample grid. Sum residual is a warning, not
    a universal separator quality metric (some models don't produce all stems).
    """
    if len(stems) < 2:
        raise ValueError('Provide at least two complementary stem files')
    with sf.SoundFile(mix) as m:
        meta = (len(m), m.samplerate, m.channels)
    handles = [sf.SoundFile(p) for p in stems]
    try:
        if any((len(h), h.samplerate, h.channels) != meta for h in handles):
            raise ValueError('Stem sample grids do not match original')
        signal_power = residual_power = 0.0
        with sf.SoundFile(mix) as source:
            while True:
                x = source.read(65536, dtype='float64', always_2d=True)
                if not len(x): break
                y = sum((s.read(len(x), dtype='float64', always_2d=True) for s in handles))
                if not np.isfinite(y).all() or not np.isfinite(x).all():
                    raise ValueError('NaN or Inf in stems/mix')
                signal_power += float(np.sum(x*x))
                residual_power += float(np.sum((x-y)**2))
        err_db = 10*np.log10((residual_power+1e-30)/(signal_power+1e-30))
        return {"source": str(mix), "sha256": sha256(mix), "stems": [str(x) for x in stems],
                "relative_reconstruction_error_db": float(err_db),
                "threshold_db": max_error_db,
                "status": "PASS" if err_db <= max_error_db else "REVIEW",
                "automatic_remix_approved": False}
    finally:
        for h in handles: h.close()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='action', required=True)
    s = sub.add_parser('separate')
    for k in ('config','checkpoint','input_folder','output_folder'):
        s.add_argument('--'+k.replace('_','-'), required=True, type=Path)
    s.add_argument('--model-type', default='bs_roformer')
    s.add_argument('--device-ids', type=int, default=0)
    s.add_argument('--force-cpu',action='store_true')
    s.add_argument('--dry-run',action='store_true')
    v = sub.add_parser('qc')
    v.add_argument('--mix',required=True,type=Path)
    v.add_argument('--stems',required=True,nargs='+',type=Path)
    a = p.parse_args()
    if a.action == 'qc':
        print(json.dumps(validate_reconstruction(a.mix, a.stems), indent=2));return
    cmd = separation_command(model_type=a.model_type,config=a.config,checkpoint=a.checkpoint,
              input_folder=a.input_folder,output_folder=a.output_folder,
              device_ids=a.device_ids,force_cpu=a.force_cpu)
    if a.dry_run:
        print(json.dumps({"status":"DRY_RUN","command":cmd},indent=2));return
    a.output_folder.mkdir(parents=True,exist_ok=True)
    subprocess.run(cmd, check=True)

if __name__ == '__main__': main()