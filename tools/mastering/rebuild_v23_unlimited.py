#!/usr/bin/env python3
"""Rebuild an UNLIMITED Golden Teeth v2.3 candidate from its original source/stems.
Does not depend on, or modify, existing limited masters. No neural inference.
A rebuilt float file must be compared with approved v2.3 before promotion.
"""
from __future__ import annotations
import argparse, hashlib, json, math, subprocess, time
from pathlib import Path
from contextlib import ExitStack
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt, stft, istft
from scipy.ndimage import gaussian_filter1d, maximum_filter1d, minimum_filter1d
from pedalboard import Pedalboard, PeakFilter, HighShelfFilter

NAMES=('drums','bass','other','piano','guitar','vocals')

def sha256(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for block in iter(lambda:f.read(1<<20),b''):h.update(block)
 return h.hexdigest()

def probe(p):
 with sf.SoundFile(p) as f:return (f.frames,f.samplerate,f.channels)

def cmd(a):
 subprocess.run(a,check=True,timeout=900)

def resample_original(original, target):
 if not target.exists():
  cmd(['ffmpeg','-v','error','-nostdin','-y','-i',str(original),'-ar','44100','-ac','2','-c:a','pcm_f32le',str(target)])

def reconstruct_qc(src,paths, sr, num):
 se=ee=ss=cs=0.; local=[]
 with ExitStack() as e:
  x=e.enter_context(sf.SoundFile(src)); st=[e.enter_context(sf.SoundFile(p)) for p in paths.values()]
  for pos in range(0,num,sr*10):
   n=min(sr*10,num-pos);a=x.read(n,dtype='float64',always_2d=True)
   b=sum((f.read(n,dtype='float64',always_2d=True) for f in st),np.zeros_like(a))
   d=float(np.sum((a-b)**2));s=float(np.sum(a*a));se+=s;ee+=d;ss+=float(np.sum(b*b));cs+=float(np.sum(a*b))
   local.append({'start':round(pos/sr,3),'error_db':round(10*math.log10((d+1e-40)/(s+1e-40)),3)})
 return {'global_error_db':round(10*math.log10(ee/se),3),'worst_window_db':max(x['error_db'] for x in local),'correlation':cs/math.sqrt(ss*se),'windows':local}

def boards():
 return {
  'drums':Pedalboard([PeakFilter(cutoff_frequency_hz=65,gain_db=0.55,q=0.85),PeakFilter(cutoff_frequency_hz=430,gain_db=-0.25,q=0.8),HighShelfFilter(cutoff_frequency_hz=8700,gain_db=0.48,q=0.7)]),
  'bass':Pedalboard([PeakFilter(cutoff_frequency_hz=95,gain_db=.35,q=.75),PeakFilter(cutoff_frequency_hz=320,gain_db=-.35,q=.8)]),
  'other':Pedalboard([PeakFilter(cutoff_frequency_hz=330,gain_db=-.4,q=.85),PeakFilter(cutoff_frequency_hz=2900,gain_db=.28,q=.9),HighShelfFilter(cutoff_frequency_hz=9100,gain_db=.18,q=.7)])
 }

def baseline(src,paths,out,n,sr):
 fx=boards();first={k:True for k in fx}
 sos=butter(4,700,btype='highpass',fs=sr,output='sos');zi=np.zeros((sos.shape[0],2))
 with ExitStack() as stack:
  f=stack.enter_context(sf.SoundFile(src))
  ss={k:stack.enter_context(sf.SoundFile(p)) for k,p in paths.items()}
  w=stack.enter_context(sf.SoundFile(out,'w',samplerate=sr,channels=2,subtype='FLOAT'))
  for pos in range(0,n,32768):
   a=f.read(min(32768,n-pos),dtype='float64',always_2d=True);d=np.zeros_like(a)
   for name,stream in ss.items():
    s=stream.read(len(a),dtype='float32',always_2d=True)
    if name in fx:
     processed=np.asarray(fx[name](s.T.copy(),sr,reset=first[name]),dtype='float64').T
     first[name]=False
     if name=='other':
      side=(processed[:,0]-processed[:,1])*.5
      filtered,zi=sosfilt(sos,side,zi=zi)
      dd=.075*filtered
      processed[:,0]+=dd;processed[:,1]-=dd
     d+=processed-s.astype('float64')
   y=a+d
   if not np.isfinite(y).all():raise ValueError('Invalid output')
   w.write(y.astype('float32'))

def bell(f,left,right,slope=0.12):
 f=np.maximum(f,1.0)
 def sig(x):return 1.0/(1.0+np.exp(-np.clip(x,-60.,60.)))
 return sig(np.log(f/left)/slope)*sig(np.log(right/f)/slope)

def activity(z,f,lo,hi):
 mag=np.mean(np.abs(z),axis=0)
 band=mag[(f>=lo)&(f<=hi)]
 env=np.sum(band**2,axis=0) if len(band) else np.zeros(mag.shape[1])
 env=gaussian_filter1d(env,2.0)
 a=minimum_filter1d(env,size=23,mode='nearest')
 b=maximum_filter1d(env,size=23,mode='nearest')
 g=np.clip((env-a)/(b-a+1e-12),0,1)
 return gaussian_filter1d(g,.9)

def split_drums(audio,sr,nfft=2048,hop=512):
 f,_,z=stft(audio.T,fs=sr,nperseg=nfft,noverlap=nfft-hop,boundary='zeros',padded=True,axis=-1)
 low=activity(z,f,35,210);mid=activity(z,f,150,4000);high=activity(z,f,5100,15000)
 wk=.78*bell(f,30,215)[:,None]*(.30+.70*low)[None,:]
 ws=.72*(.50*bell(f,145,590)+.75*bell(f,1700,5300))[:,None]*(.30+.70*mid)[None,:]
 wh=.77*bell(f,5400,15000)[:,None]*(.24+.76*high)[None,:]
 wc=.28*bell(f,4400,17700)[:,None]*(.70-.35*high)[None,:]
 weight=np.stack([wk,ws,wh,wc],axis=0)
 s=weight.sum(axis=0)
 weight*=np.minimum(1.,.92/(s+1e-12))[None,:,:]
 out={}
 for i,name in enumerate(('kick','snare_clap','hats','cymbals')):
  _,wave=istft(z*weight[i][None,:,:],fs=sr,nperseg=nfft,noverlap=nfft-hop,boundary=True,input_onesided=True,time_axis=-1,freq_axis=-2)
  out[name]=wave.T[:len(audio)].astype('float64')
 out['residual']=audio-sum(out.values())
 return out

def onset_envelope(s,sr):
 hop=max(1,round(sr*.005));n=len(s);ix=np.arange(0,n,hop)
 energy=np.array([np.mean(s[i:min(n,i+hop)]**2) for i in ix])
 short=np.sqrt(np.maximum(gaussian_filter1d(energy,1.6,mode='nearest'),0))
 long=np.sqrt(np.maximum(gaussian_filter1d(energy,20.0,mode='nearest'),0))
 peak=float(np.max(long))
 if peak<1e-9:return np.zeros(n,dtype='float64')
 novelty=np.clip((short/(long+1e-9)-1.)/.85,0,1)
 activity=np.clip((short/peak-.017)/.13,0,1)
 frame=np.clip(gaussian_filter1d(novelty*activity,1.),0,1)
 return np.interp(np.arange(n),ix,frame,left=frame[0],right=frame[-1])

def linked_delta(parts,sr):
 gains={'kick':(.4,.13),'hats':(.36,.38),'snare_clap':(-.44,-.18),'cymbals':(.10,0)}
 out=np.zeros_like(parts['kick'])
 for name,(body,attack) in gains.items():
  env=onset_envelope(parts[name],sr) if attack else 0.
  gain=body+attack*env
  if isinstance(gain,np.ndarray):out+=parts[name]*np.expm1(np.log(10)/20*gain)[:,None]
  else:out+=parts[name]*math.expm1(math.log(10)/20*gain)
 return out

def v23_delta(base,drums,output,n,sr):
 # 8 second batches with 600 ms source context, identical to upstream rendering plan.
 delta_power=base_power=0.;peak=0.;max_null=0.
 with sf.SoundFile(base) as b,sf.SoundFile(drums) as d,sf.SoundFile(output,'w',samplerate=sr,channels=2,subtype='FLOAT') as w:
  for pos in range(0,n,sr*8):
   end=min(n,pos+sr*8);lo=max(0,pos-int(.60*sr));hi=min(n,end+int(.60*sr))
   d.seek(lo);buf=d.read(hi-lo,dtype='float64',always_2d=True)
   parts=split_drums(buf,sr)
   max_null=max(max_null,float(np.max(np.abs(sum(parts.values())-buf))))
   delta=linked_delta(parts,sr)[pos-lo:end-lo]
   old=b.read(end-pos,dtype='float64',always_2d=True);y=old+delta
   if not np.isfinite(y).all():raise RuntimeError('Nonfinite samples')
   delta_power+=float(np.sum(delta**2));base_power+=float(np.sum(old**2))
   peak=max(peak,float(np.max(abs(y))))
   w.write(y.astype('float32'))
 return {'peak':peak,'delta_relative_db':10*math.log10(delta_power/base_power),'max_null_abs':max_null}

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--root',type=Path,default=Path('/mnt/data'))
 ap.add_argument('--output',type=Path,required=True)
 a=ap.parse_args();root=a.root
 if a.output.exists() and any(a.output.iterdir()):
  raise FileExistsError('Refusing stale cache/overwrite: choose a fresh empty --output directory')
 a.output.mkdir(parents=True,exist_ok=True)
 orig=root/'LOFI HOUSE - deepsmeeth - golden teeth - Treblo.wav'; paths={s:root/f'{s} golden teeth.wav' for s in NAMES}
 allpaths=[orig,*paths.values()]; hashes={str(p.name):sha256(p) for p in allpaths}
 n,sr,ch=probe(paths['drums']);assert sr==44100 and ch==2
 assert all(probe(p)==(n,sr,ch) for p in paths.values())
 source=a.output/'source_resampled_44k_float32.wav';resample_original(orig,source)
 assert probe(source)==(n,sr,ch)
 qc=reconstruct_qc(source,paths,sr,n)
 print('RECONSTRUCTION:',qc['global_error_db'],qc['worst_window_db'],flush=True)
 if qc['global_error_db']>-32 or qc['worst_window_db']>-23:raise RuntimeError('Unmatched original+stems')
 baseline_path=a.output/'base_v21_unlimited_float32.wav';raw=a.output/'GT_v23_unlimited_rebuilt_float32.wav'
 if not baseline_path.exists():baseline(source,paths,baseline_path,n,sr)
 print('BASELINE READY',flush=True)
 if not raw.exists():stats=v23_delta(baseline_path,paths['drums'],raw,n,sr)
 else:stats={'reused':True}
 assert probe(raw)==(n,sr,ch)
 assert {str(p.name):sha256(p) for p in allpaths}==hashes
 report={'status':'RECONSTRUCTED_UNLIMITED_CANDIDATE_NOT_YET_REFERENCE_VALIDATED','original_hashes':hashes,'resample_sha256':sha256(source),'baseline_sha256':sha256(baseline_path),'v23_rebuilt_sha256':sha256(raw),'stem_reconstruction_qc':qc,'delta_stats':stats,'sr':sr,'frames':n,'note':'Rebuilt from GitHub algorithms, not an original saved premaster; verify against v2.3 approved master before trusting.'}
 (a.output/'rebuild_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
 print('RESULT:',json.dumps({k:report[k] for k in ('status','v23_rebuilt_sha256','delta_stats')},indent=2),flush=True)
if __name__=='__main__':main()