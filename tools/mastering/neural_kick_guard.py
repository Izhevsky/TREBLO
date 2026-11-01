#!/usr/bin/env python3
"""Guarded candidate from REAL 5 DrumSep neural stems. Generates UNMASTERED float32.

This is deliberately kick-only: synthetic v2.7 test showed poor HH/ride isolation.
It does NOT assert neural purity on Golden Teeth; never auto-promote to final master.
Does not download model weights or upload any user files.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from neural_drumsep_bridge import STEMS, QC, render_delta, apply_delta, sha256

DEFAULT_KICK_DB = 0.25


def build_candidate(drums:Path, baseline_unlimited:Path, predicted:Path,workdir:Path,
                    *, kick_db:float=DEFAULT_KICK_DB):
    drums=Path(drums).resolve();baseline_unlimited=Path(baseline_unlimited).resolve()
    predicted=Path(predicted).resolve();workdir=Path(workdir).resolve()
    if not 0 <= kick_db <= .35:raise ValueError('Kick gain must be 0..0.35 dB')
    paths={k:predicted/(k+'.wav') for k in STEMS}
    for p in (drums,baseline_unlimited,*paths.values()):
        if not p.is_file():raise FileNotFoundError(p)
    sources={str(p.resolve()) for p in (drums,baseline_unlimited,*paths.values())}
    delta=workdir/'neural_kick_delta_float32.wav'; mix=workdir/'neural_kick_candidate_UNMASTERED_float32.wav'
    report=workdir/'neural_kick_qc.json'
    if any(str(p.resolve()) in sources for p in (delta,mix,report)):
        raise ValueError('Never overwrite any source')
    if any(p.exists() for p in (delta,mix,report)):
        raise FileExistsError('Refusing overwrite: use a fresh work directory')
    workdir.mkdir(parents=True,exist_ok=True)
    gains={k:(kick_db if k=='kick' else 0.0) for k in STEMS}
    # Extra conservative guard, compared with old general-purpose 5-stem mix.
    q=render_delta(drums,paths,delta,report,qc=QC(max_error_db=-15.0,
                    max_sum_to_source_ratio=1.65,max_delta_db=-28.0,gain_limit_db=0.35),changes=gains)
    applied=apply_delta(baseline_unlimited,delta,mix,max_difference_db=-28.0)
    result={**q,'candidate_sha256':sha256(mix),'premaster_status':'UNMASTERED_FLOAT32',
      'human_listening_required':True,'auto_replace_prior_versions':False,
      'policy':'Only neural kick +0..0.35 dB; HH, snare, toms, cymbals are UNCHANGED',
      'mix_qc':applied}
    report.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--drums',required=True,type=Path)
    p.add_argument('--baseline-unlimited',required=True,type=Path)
    p.add_argument('--predicted-dir',required=True,type=Path)
    p.add_argument('--workdir',required=True,type=Path)
    p.add_argument('--kick-gain-db',type=float,default=DEFAULT_KICK_DB)
    a=p.parse_args()
    print(json.dumps(build_candidate(a.drums,a.baseline_unlimited,a.predicted_dir,a.workdir,kick_db=a.kick_gain_db),indent=2))
if __name__=='__main__':main()