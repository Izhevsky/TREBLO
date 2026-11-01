#!/usr/bin/env python3
"""Build fixed-order equal-LUFS A/B WAV/FLAC without an extra limiter."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import sys
import tempfile
import numpy as np
import soundfile as sf

# Invocation works from any cwd.
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from tools.mastering.astra_pedalboard import scan_loudness


def create_ab(reference: Path, processed: Path, output: Path,
              positions: list[float], seconds: float = 12.0, ffmpeg: str = 'ffmpeg') -> dict:
    with sf.SoundFile(reference) as x, sf.SoundFile(processed) as y:
        if (x.samplerate,x.channels,len(x)) != (y.samplerate,y.channels,len(y)):
            raise ValueError('A/B requires equal sample rates, channels and exact frame counts')
        rate=x.samplerate
        if x.channels != 2: raise ValueError('A/B supports stereo only')
        frames=int(round(seconds*rate))
        if any(p < 0 or int(round(p*rate))+frames > len(x) for p in positions):
            raise ValueError('Invalid A/B window')
        with tempfile.TemporaryDirectory() as t:
            t=Path(t)
            pairs=[]
            concat=[]
            gap=np.zeros((int(.75*rate),2),np.float32)
            for i,pos in enumerate(positions):
                idx=int(round(pos*rate));x.seek(idx);y.seek(idx)
                a=x.read(frames,dtype='float32',always_2d=True)
                b=y.read(frames,dtype='float32',always_2d=True)
                pa,pb=t/f'a{i}.wav',t/f'b{i}.wav'
                sf.write(pa,a,rate,subtype='FLOAT');sf.write(pb,b,rate,subtype='FLOAT')
                la=scan_loudness(pa,ffmpeg)['input_i']
                lb=scan_loudness(pb,ffmpeg)['input_i']
                # Both are attenuated to same level. Avoid any extra peak limiting.
                target=min(la,lb)-4.0
                a=a*10**((target-la)/20)
                b=b*10**((target-lb)/20)
                fade=min(int(.01*rate),len(a)//2)
                if fade:
                    ramp=np.linspace(0,1,fade,endpoint=True,dtype=np.float32)[:,None]
                    for part in (a,b):
                        part[:fade]*=ramp
                        part[-fade:]*=ramp[::-1]
                if max(float(np.max(abs(a))),float(np.max(abs(b)))) >= 1.0:
                    raise RuntimeError('A/B would clip; lower target before proceeding')
                concat.extend([a,gap,b,gap])
                pairs.append({'start_s':pos,'length_s':seconds,'lufs_a_before':la,
                              'lufs_b_before':lb,'target_lufs':target})
            output.parent.mkdir(parents=True,exist_ok=True)
            with sf.SoundFile(output,'w',samplerate=rate,channels=2,
                              format='FLAC',subtype='PCM_24') as f:
                for part in concat:f.write(part)
    return {'output':str(output),'pairs':pairs,'comparison':'KNOWN_A_THEN_B','gain_type':'CONSTANT','no_limiter':True}

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('reference',type=Path);p.add_argument('processed',type=Path)
    p.add_argument('output',type=Path);p.add_argument('--start',type=float,action='append',required=True)
    p.add_argument('--seconds',type=float,default=12.)
    a=p.parse_args()
    print(json.dumps(create_ab(a.reference,a.processed,a.output,a.start,a.seconds),indent=2))