#!/usr/bin/env python3
"""Golden Teeth v2.2 conservative drum-band delta from aligned drums stem.

Astra v2.1 baseline processing is applied once from unmastered source/stems,
then bounded kick/snare-clap/hat/cymbal sub-stem deltas are added. No new beats.
No neural model is used. Stereo sub-stems contain bleed, therefore not isolated
instruments. The original and six WAV stems are NEVER modified.
"""
from pathlib import Path
import sys, hashlib, json, math, shutil, tempfile
from dataclasses import asdict
import numpy as np
import soundfile as sf
from drum_substem_dsp import split_drums,remix_delta,DspProfile
sys.path.insert(0,str(Path(__file__).resolve().parent))
from stem_delta_rework import STEM_NAMES, validate_stems, build_delta_remix
from astra_pedalboard import shell, scan_loudness, independently_scan_ebur128, sha256, sample_count, master_premaster, convert_float_to_pcm, Config


def run(original:Path, stemdir:Path, out:Path, profile:DspProfile=DspProfile(), preview_only=False):
    out.parent.mkdir(exist_ok=True, parents=True)
    drums=stemdir/'drums golden teeth.wav'
    stems={n:stemdir/f'{n} golden teeth.wav' for n in STEM_NAMES}
    hashes={n:sha256(p) for n,p in {'original':original,**stems}.items()}
    with tempfile.TemporaryDirectory(prefix='treblo_v22_') as td:
        tmp=Path(td); working=tmp/'source_44100.wav'
        shell(['ffmpeg','-v','error','-nostdin','-y','-i',str(original),'-ar','44100','-ac','2','-c:a','pcm_f32le',str(working)],900)
        count,rate,ch=sample_count(drums)
        if sample_count(working)!=(count,rate,2): raise RuntimeError('Source/stem length mismatch')
        qc=validate_stems(working,stems)
        if qc['global_reconstruction_error_db']>-32 or qc['max_window_error_db']>-23:
            raise RuntimeError('Aligned stems failed reconstruction gate')
        baseline=tmp/'baseline_v21_float.wav'
        build_delta_remix(working,stems,baseline,count,rate,32768)
        n=count if not preview_only else min(count, int(rate*42))
        raw=tmp/'v22_raw.wav'
        batch=rate*8
        margin=int(0.6*rate)
        sum_err=0.0; max_err=0.0; input_energy=0.0; delta_energy=0.0; peak=0.0
        with sf.SoundFile(baseline) as base, sf.SoundFile(drums) as source, sf.SoundFile(raw,'w',samplerate=rate,channels=2,subtype='FLOAT') as dest:
            for pos in range(0,n,batch):
                end=min(n,pos+batch)
                lo=max(0,pos-margin);hi=min(count,end+margin)
                source.seek(lo)
                buf=source.read(hi-lo,dtype='float64',always_2d=True)
                parts=split_drums(buf,rate)
                rec=sum(parts.values())
                err=float(np.max(abs(rec-buf)))
                max_err=max(max_err,err)
                # remove analysis context: compare exact same sample grid.
                i=pos-lo;j=end-lo
                delta=remix_delta(parts,**asdict(profile))[i:j]
                old=base.read(end-pos,dtype='float64',always_2d=True)
                output=old+delta
                if not np.isfinite(output).all(): raise RuntimeError('Nonfinite output')
                peak=max(peak,float(np.max(np.abs(output))))
                delta_energy+=float(np.sum(delta*delta));input_energy+=float(np.sum(old*old))
                dest.write(output.astype('float32'))
        if peak<1e-9:raise RuntimeError('Silence')
        premaster=tmp/'PREMASTER_float32.wav'
        g=10**(-6/20)/peak
        shell(['ffmpeg','-v','error','-nostdin','-y','-i',str(raw),'-af',f'volume={g:.14f}', '-c:a','pcm_f32le',str(premaster)],900)
        if sample_count(premaster)!=(n,rate,2):raise RuntimeError('Grid mismatch premaster')
        pre=scan_loudness(premaster,'ffmpeg')
        cfg=Config(input=premaster,output=out,target_lufs=-13.7,true_peak_ceiling=-1.4)
        history=[]
        for it in range(4):
            fc=tmp/f'master_float_{it}.wav'
            ceiling=-1.55-0.16*it
            master_premaster(premaster,fc,cfg,pre['input_i'],ceiling)
            candidate=tmp/'candidate.flac'
            convert_float_to_pcm(fc,candidate,'ffmpeg',24)
            qc_final=scan_loudness(candidate,'ffmpeg')
            history.append({'ceiling':ceiling,'true_peak':qc_final['input_tp']})
            if qc_final['input_tp']<=-1.35:break
        else:raise RuntimeError('True peak check fails')
        if sample_count(candidate)!=(n,rate,2):raise RuntimeError('Master grid mismatch')
        if any(sha256(p)!=hashes[k] for k,p in {'original':original,**stems}.items()):raise RuntimeError('Modified input')
        shutil.copyfile(candidate,out)
        compatible=out.with_name(out.stem+'_16bit.flac')
        convert_float_to_pcm(fc,compatible,'ffmpeg',16)
        assert sample_count(compatible)==(n,rate,2)
        report={
            'version':'TREBLO_Astra_Drum_Substem_DSP_v2.2',
            'stage':'Experimental; not user-approved',
            'note':'Frequency/transient proxy STEMS, NOT neural stem separation and NOT guaranteed instrument isolation',
            'base':'Astra Stem Delta Rework v2.1 from original and six source stems (not remastering an already limited file)',
            'source_hashes_sha256':hashes,'stem_validation':{
                'correlation':qc['correlation'],'global_error_db':qc['global_reconstruction_error_db'],'max_window_error_db':qc['max_window_error_db']},
            'substem_reconstruction_max_absolute_error_float64':max_err,
            'substem_delta_rms_relative_to_baseline_db':10*np.log10(max(delta_energy,1e-50)/max(input_energy,1e-50)),
            'band_gain_db':asdict(profile),'duration_seconds':n/rate,
            'final':{**qc_final,'independent_ebur128_lufs':independently_scan_ebur128(out,'ffmpeg'),
                     'rate':rate,'frames':n,'master24_sha256':sha256(out),'master16_sha256':sha256(compatible)},
            'true_peak_ceiling_attempts':history,
            'listen_verdict':'NOT_PERFORMED',
            'neural_model':'NOT_AVAILABLE'}
        out.with_suffix('.qc.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
        return report

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('--original',type=Path,required=True)
    p.add_argument('--stemdir',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--preview-only',action='store_true')
    args=p.parse_args()
    print(json.dumps(run(args.original,args.stemdir,args.output,preview_only=args.preview_only)['final'],indent=2))