#!/usr/bin/env python3
"""TREBLO v3.0: gate neural provenance BEFORE v2.8 mastering and AB.

Requires real DrumSep outputs from drumsep_6stem_float_bridge.py and the
original INFERENCE_REPORT.json in the same stem directory. No checkpoint
or audio is uploaded. Does not auto-accept a master on behalf of a listener.
"""
from pathlib import Path
import argparse,json
from neural_provenance_gate import check,doctor,digest

def render_guarded(drums:Path, neural_dir:Path, v23_unlimited:Path,
                   v23_master:Path, studio_rework:Path,workdir:Path,
                   *,kick_db:float=.25,target_lufs:float=-13.7,true_peak:float=-1.4,
                   make_ab:bool=True):
    # Verify provenance and reconstruction BEFORE any new directory is created.
    if not (0. <= kick_db <= .35):raise ValueError('v3 only allows kick_db 0..0.35')
    if Path(workdir).exists():raise FileExistsError('Workdir must be new')
    gate=check(drums,neural_dir)
    from neural_master_pipeline import source_preflight,render
    sources=source_preflight(drums,v23_unlimited,v23_master,studio_rework)
    if sources['source_sha256']['drums']!=gate['drums_sha256']:
        raise ValueError('Drums hash changed after neural inference')
    result=render(drums,v23_unlimited,v23_master,studio_rework,neural_dir,workdir,
                  kick_db=kick_db,target_lufs=target_lufs,true_peak=true_peak,make_ab=make_ab)
    # Recheck after processing, prior to declaring the experiment verifiable.
    if digest(Path(drums))!=gate['drums_sha256']:
        raise RuntimeError('Source modified during mastering')
    finish=Path(workdir)/'PROVENANCE_QC.json'
    finish.write_text(json.dumps(gate,ensure_ascii=False,indent=2),encoding='utf-8')
    return {'render':result,'provenance_gate':gate,'candidate_status':'EXPERIMENTAL_AWAITING_LISTENING'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['doctor','check','render'])
    parser.add_argument('--drums',required=True,type=Path)
    parser.add_argument('--unlimited',type=Path)
    parser.add_argument('--predicted',type=Path)
    parser.add_argument('--v23-master',type=Path)
    parser.add_argument('--studio-rework',type=Path)
    parser.add_argument('--workdir',type=Path)
    parser.add_argument('--model-cache',type=Path,default=Path.home()/'.cache/mdxnet-infer')
    parser.add_argument('--kick-db',type=float,default=.25)
    parser.add_argument('--skip-ab',action='store_true')
    args=parser.parse_args()
    if args.mode=='doctor':
        if not args.unlimited:parser.error('--unlimited is required for doctor')
        r=doctor(args.drums,args.unlimited,args.model_cache)
    elif args.mode=='check':
        if not args.predicted:parser.error('--predicted is required for check')
        r=check(args.drums,args.predicted)
    else:
        for field in ('unlimited','predicted','v23_master','studio_rework','workdir'):
            if getattr(args,field) is None:parser.error('--'+field.replace('_','-')+' is required for render')
        r=render_guarded(args.drums,args.predicted,args.unlimited,args.v23_master,
                         args.studio_rework,args.workdir,kick_db=args.kick_db,make_ab=not args.skip_ab)
    print(json.dumps(r,ensure_ascii=False,indent=2,default=str))
if __name__=='__main__':main()