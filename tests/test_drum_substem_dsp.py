import unittest
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"/"mastering"))
from drum_substem_dsp import split_drums, remix_delta, DspProfile

class TestDrumSubstems(unittest.TestCase):
    def setUp(self):
        sr=44100;t=np.arange(sr*2)/sr
        a=0.48*np.sin(2*np.pi*67*t)*np.exp(-14*(t%0.5))
        b=0.1*np.sin(2*np.pi*9200*t)*np.exp(-40*(t%0.25))
        x=a+b
        self.x=np.column_stack([x,x*.9]);self.sr=sr
    def test_exact_sum(self):
        p=split_drums(self.x,self.sr)
        self.assertLess(np.max(np.abs(sum(p.values())-self.x)),1e-9)
    def test_neutral_delta(self):
        p=split_drums(self.x,self.sr)
        self.assertEqual(np.max(np.abs(remix_delta(p,0,0,0,0))),0)
    def test_band_separation_proxy(self):
        p=split_drums(self.x,self.sr)
        # The kick proxy has strong low-frequency content, hats higher.
        import scipy.signal as sig
        def frac_high(x):
            f,a=sig.welch(x[:,0],self.sr,nperseg=2048)
            return sum(a[f>5000])/sum(a)
        self.assertLess(frac_high(p['kick']),frac_high(p['hats']))
    def test_invalid_shape(self):
        with self.assertRaises(ValueError):split_drums(self.x[:,0],self.sr)
    def test_limits(self):
        with self.assertRaises(ValueError):DspProfile(hats_db=6.)
    def test_center(self):
        p=split_drums(self.x,self.sr)
        self.assertLess(np.max(np.abs(p['kick'][:,1]-.9*p['kick'][:,0])),1e-6)
if __name__=='__main__':unittest.main()