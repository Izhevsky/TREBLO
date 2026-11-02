import sys,unittest,tempfile
from pathlib import Path
import numpy as np
import soundfile as sf
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from rebuild_v23_unlimited import bell,split_drums,linked_delta,v23_delta,probe
class TestV23Rebuild(unittest.TestCase):
 def setUp(self):
  self.sr=44100
  rng=np.random.default_rng(42); t=np.arange(44100)/44100
  x=.035*np.sin(2*np.pi*65*t)*np.exp(-5*t)+.005*rng.normal(size=len(t))
  self.audio=np.column_stack([x,x*.97]).astype('float64')
 def test_mask_bounded(self):
  f=np.linspace(0,22050,300)
  v=bell(f,30,215)
  self.assertTrue(np.isfinite(v).all());self.assertTrue(np.all((v>=0)&(v<=1)))
 def test_exact_proxy_reconstruction(self):
  d=split_drums(self.audio,self.sr)
  self.assertEqual(len(d),5)
  self.assertLess(np.max(abs(sum(d.values())-self.audio)),1e-14)
 def test_linked_delta_small(self):
  d=split_drums(self.audio,self.sr)
  delta=linked_delta(d,self.sr)
  self.assertEqual(delta.shape,self.audio.shape)
  self.assertTrue(np.isfinite(delta).all())
  self.assertLess(np.sqrt(np.mean(delta*delta)/np.mean(self.audio*self.audio)),.15)
 def test_stereo_preserves_link(self):
  d=split_drums(self.audio,self.sr)
  delta=linked_delta(d,self.sr)
  self.assertLess(float(np.max(abs(delta[:,1]-.97*delta[:,0]))),1e-7)
 def test_real_wav_float_render_no_clipping(self):
  with tempfile.TemporaryDirectory() as td:
   td=Path(td)
   base=td/'baseline.wav';drums=td/'drums.wav';out=td/'out.wav'
   sf.write(base,self.audio,self.sr,subtype='FLOAT')
   sf.write(drums,self.audio,self.sr,subtype='FLOAT')
   q=v23_delta(base,drums,out,len(self.audio),self.sr)
   self.assertEqual(probe(out),(len(self.audio),self.sr,2))
   self.assertGreater(q['peak'],0)
   self.assertLess(q['max_null_abs'],1e-14)
 def test_deterministic_delta(self):
  parts=split_drums(self.audio,self.sr)
  a=linked_delta(parts,self.sr);b=linked_delta(parts,self.sr)
  np.testing.assert_array_equal(a,b)
if __name__=='__main__':unittest.main()