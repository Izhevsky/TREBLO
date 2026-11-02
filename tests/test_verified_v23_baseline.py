import unittest,sys,tempfile,os
from pathlib import Path
import numpy as np,soundfile as sf
_here=Path(__file__).resolve().parent
sys.path.insert(0,str(_here if (_here/"verified_v23_baseline.py").exists() else _here.parent/"tools"/"mastering"))
from verified_v23_baseline import pcm_comparison,sha256,verify

class BaselineTests(unittest.TestCase):
 def test_true_pcm_identical(self):
  with tempfile.TemporaryDirectory() as d:
   x=np.random.default_rng(11).uniform(-.8,.8,(5000,2)).astype('float32')
   a=Path(d)/'a.flac';b=Path(d)/'b.flac'
   sf.write(a,x,44100,subtype='PCM_24');sf.write(b,x,44100,subtype='PCM_24')
   m=pcm_comparison(a,b)
   self.assertTrue(m['decoded_pcm_exact']);self.assertEqual(m['mismatched_channel_samples'],0)
 def test_changed_sample_detected(self):
  with tempfile.TemporaryDirectory() as d:
   x=np.zeros((600,2),dtype='float32');a=Path(d)/'a.flac';b=Path(d)/'b.flac'
   sf.write(a,x,44100,subtype='PCM_24');x[100,0]=.2;sf.write(b,x,44100,subtype='PCM_24')
   m=pcm_comparison(a,b);self.assertEqual(m['mismatched_channel_samples'],1);self.assertFalse(m['decoded_pcm_exact'])
 def test_grid_mismatch_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   x=np.zeros((600,2));a=Path(d)/'a.flac';b=Path(d)/'b.flac'
   sf.write(a,x,44100,subtype='PCM_24');sf.write(b,x,48000,subtype='PCM_24')
   with self.assertRaises(ValueError):pcm_comparison(a,b)
 def test_pcm16_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   a=Path(d)/'a.flac';sf.write(a,np.zeros((600,2)),44100,subtype='PCM_16')
   with self.assertRaises(ValueError):pcm_comparison(a,a)
 def test_no_modified_existing_dir(self):
  from verified_v23_baseline import build
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(FileExistsError):build(Path('foo'),Path('bar'),Path('baz'),Path(d))

if __name__=='__main__':unittest.main()