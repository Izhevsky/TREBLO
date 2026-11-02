from pathlib import Path
import numpy as np, soundfile as sf, subprocess,json,math,re,hashlib
import argparse
ap=argparse.ArgumentParser()
ap.add_argument('--workdir',required=True,type=Path)
ap.add_argument('--reference',required=True,type=Path)
a=ap.parse_args()
work=a.workdir.resolve()
src=work/'GT_v23_unlimited_rebuilt_float32.wav'
pre=work/'GT_v23_PREMASTER_float32.wav'
prev=a.reference.resolve()
if not src.is_file() or not prev.is_file():raise FileNotFoundError('Need rebuilt unlimited mix and a reference FLAC')

def run(args):
 p=subprocess.run(args,check=True,text=True,capture_output=True)
 return p.stderr

def scan(p):
 s=run(['ffmpeg','-nostdin','-hide_banner','-i',str(p),'-af','loudnorm=I=-24:TP=-2:LRA=7:print_format=json','-f','null','-'])
 ix=s.rfind('{\n'); q=json.JSONDecoder().raw_decode(s[ix:])[0]
 return {k:float(q[k]) for k in ('input_i','input_tp','input_lra')}
peak=0
with sf.SoundFile(src) as f:
 for b in f.blocks(blocksize=262144,dtype='float64',always_2d=True):peak=max(peak,float(np.max(abs(b))))
g=10**(-6/20)/peak
with sf.SoundFile(src) as f,sf.SoundFile(pre,'w',samplerate=f.samplerate,channels=2,subtype='FLOAT') as o:
 for b in f.blocks(blocksize=262144,dtype='float64',always_2d=True):o.write((b*g).astype('float32'))
q=scan(pre)
print('PRE',q,'PEAK',peak,flush=True)
for iteration in range(4):
 ceil=-1.55-.15*iteration;ff=10**(ceil/20)
 post=work/'post_limiter_float32.wav'
 filter=f'aresample=176400:resampler=soxr:precision=28,volume={-13.7-q["input_i"]:.7f}dB,alimiter=limit={ff:.9f}:attack=5:release=90:level=0:latency=1,aresample=44100:resampler=soxr:precision=28'
 run(['ffmpeg','-v','error','-nostdin','-y','-i',str(pre),'-af',filter,'-ac','2','-c:a','pcm_f32le',str(post)])
 candidate=work/'GT_v23_remaster_reference_check.flac'
 run(['ffmpeg','-v','error','-nostdin','-y','-i',str(post),'-af','aresample=osf=s32:dither_method=triangular:output_sample_bits=24','-c:a','flac','-sample_fmt','s32','-bits_per_raw_sample','24',str(candidate)])
 meas=scan(candidate)
 print('MASTER',iteration,meas,flush=True)
 if meas['input_tp']<=-1.35:break

comparison=[]
with sf.SoundFile(prev) as p,sf.SoundFile(candidate) as c:
 assert (p.frames,p.samplerate,p.channels)==(c.frames,c.samplerate,c.channels)
 for pos in [0,30,42,94,171,220]:
  p.seek(int(pos*44100));c.seek(int(pos*44100))
  n=min(44100*5,p.frames-int(pos*44100))
  a=p.read(n,dtype='float64',always_2d=True);b=c.read(n,dtype='float64',always_2d=True)
  correlation=float(np.sum(a*b)/math.sqrt(np.sum(a*a)*np.sum(b*b)))
  scale=float(np.sum(a*b)/np.sum(b*b))
  diff=float(10*math.log10(np.sum((a-b*scale)**2)/np.sum(a*a)))
  rellevel=float(20*math.log10(np.sqrt(np.mean(b*b))/np.sqrt(np.mean(a*a))))
  comparison.append({'start_sec':pos,'correlation':correlation,'difference_db_gain_matched':diff,'level_difference_db':rellevel})
report={'rebuild_peak':peak,'premaster_lufs':q,'reconstructed_master_lufs':meas,'comparison_with_existing_v23':comparison,'reference_validation_status':'CHECK_FIDELITY_NOT_BIT_IDENTICAL','source_reference':str(prev),'candidate_reference_check':str(candidate)}
(work/'reference_comparison_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))