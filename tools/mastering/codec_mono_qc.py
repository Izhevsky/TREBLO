#!/usr/bin/env python3
"""Non-destructive stereo->mono spectral QC with optional AAC codec preview.

For each selected active window, compare per-band energy of mono fold (L+R)/2
against the stereo power reference (L^2+R^2)/2. A negative band delta
quantifies mono cancellation, NOT a listening verdict. Defaults never fail
quiet/inactive bands. Does not change the master or upload audio.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import tempfile

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

BANDS = ((28,120),(120,500),(500,4000),(4000,15000))


def digest(path: Path) -> str:
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def inspect_windows(path:Path, starts=(0,42,94,171), seconds=12, min_band_dbfs=-65.0):
    """Window-specific power comparisons; returns evidence, not automatic DSP actions."""
    report=[]
    with sf.SoundFile(path) as f:
        if f.channels!=2:raise ValueError('Stereo file required')
        if f.samplerate not in (44100,48000,88200,96000):raise ValueError('Unsupported rate')
        sr=f.samplerate
        for start in starts:
            start=float(start)
            if start < 0 or start>=len(f)/sr:raise ValueError('Window start outside audio')
            f.seek(round(start*sr))
            x=f.read(min(round(seconds*sr), len(f)-f.tell()),dtype='float64',always_2d=True)
            if not np.isfinite(x).all():raise ValueError('Nonfinite audio')
            if len(x)<sr//2:raise ValueError('Window too short')
            # Prevent false alarms on silence; global gate based on total stereo RMS.
            stereo_power=float(np.mean(x*x))
            global_db=10*math.log10(max(stereo_power,1e-30))
            block={'start_s':start,'duration_s':len(x)/sr,'stereo_rms_dbfs':round(global_db,3),'bands':[]}
            for low,high in BANDS:
                high=min(high,0.45*sr)
                if low>=high:continue
                sos=butter(4,(low,high),btype='bandpass',fs=sr,output='sos')
                filt=sosfilt(sos,x,axis=0)
                mono=(filt[:,0]+filt[:,1])*0.5
                st_power=float(np.mean(filt*filt))
                mono_power=float(np.mean(mono*mono))
                band_rms_db=10*math.log10(max(st_power,1e-30))
                active=band_rms_db>min_band_dbfs and global_db>min_band_dbfs
                delta_db=10*math.log10(max(mono_power,1e-30)/max(st_power,1e-30))
                block['bands'].append({'hz':f'{low:g}-{high:g}',
                    'stereo_rms_dbfs':round(band_rms_db,3),'mono_loss_db':round(delta_db,3),
                    'active':active,'warning':bool(active and delta_db < -6.0)})
            report.append(block)
    return report


def loudness(path:Path,ffmpeg='ffmpeg'):
    c=subprocess.run([ffmpeg,'-hide_banner','-nostdin','-i',str(path),
      '-af','loudnorm=I=-24:TP=-2:LRA=7:print_format=json','-f','null','-'],
      capture_output=True,text=True,check=True,timeout=600)
    offset=c.stderr.rfind('{\n')
    if offset<0:raise RuntimeError('loudnorm JSON missing')
    j=json.JSONDecoder().raw_decode(c.stderr[offset:])[0]
    return {k:float(j[k]) for k in ('input_i','input_tp','input_lra')}


def codec_preview(source:Path, out:Path, ffmpeg='ffmpeg', start=42.0, seconds=30.0):
    if source.resolve()==out.resolve():raise ValueError('Never overwrite source')
    out.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run([ffmpeg,'-hide_banner','-nostdin','-loglevel','error','-y',
      '-ss',str(start),'-i',str(source),'-t',str(seconds),'-map','0:a:0',
      '-ac','2','-c:a','aac','-b:a','128k',str(out)],check=True,timeout=120)
    if out.stat().st_size<1000:raise RuntimeError('Preview empty')
    return loudness(out,ffmpeg)


def run(source:Path, output:Path, preview:Path|None=None, starts=(0,42,94,171),ffmpeg='ffmpeg'):
    if not source.is_file():raise FileNotFoundError(source)
    if output.resolve()==source.resolve():raise ValueError('QC must not overwrite source')
    before=digest(source)
    windows=inspect_windows(source,starts=starts)
    result={'source':str(source),'source_sha256':before,
      'mono_window_qc':windows,
      'warnings':[{'start_s':w['start_s'],'band':b['hz'],'loss_db':b['mono_loss_db']}
                  for w in windows for b in w['bands'] if b['warning']],
      'limitations':'Band cancellation is an engineering metric, not proof of audible degradation.'}
    if preview:
        result['aac_preview']={'file':str(preview),'metrics':codec_preview(source,preview,ffmpeg)}
    if digest(source)!=before:raise RuntimeError('Source changed')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source',type=Path);ap.add_argument('report',type=Path)
    ap.add_argument('--aac-preview',type=Path);ap.add_argument('--starts',type=float,nargs='+',default=[0,42,94,171]);ap.add_argument('--ffmpeg',default='ffmpeg')
    a=ap.parse_args();r=run(a.source,a.report,a.aac_preview,tuple(a.starts),a.ffmpeg)
    print(json.dumps({'warnings':r['warnings'],'report':str(a.report)},ensure_ascii=False))
if __name__=='__main__':main()