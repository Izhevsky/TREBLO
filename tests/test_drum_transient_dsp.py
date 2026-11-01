import unittest, sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/mastering'))
from drum_transient_dsp import Profile,onset_envelope,linked_delta

class TransientTests(unittest.TestCase):
    def setUp(self):
        rng=np.random.default_rng(42)
        self.sr=44100
        n=44100
        sig=rng.normal(0,.01,(n,2))
        for pos in [5000,15000,32000]:sig[pos:pos+300] += .20*np.hanning(300)[:,None]
        self.parts={k:sig * q for k,q in [('kick',.8),('snare_clap',.42),('hats',.22),('cymbals',.12)]}
    def test_linked_envelope_range(self):
        e=onset_envelope(self.parts['kick'],self.sr)
        self.assertTrue(np.isfinite(e).all());self.assertGreaterEqual(e.min(),0);self.assertLessEqual(e.max(),1)
    def test_no_op(self):
        p=Profile(0,0,0,0,0,0,0,0)
        self.assertTrue(np.array_equal(linked_delta(self.parts,self.sr,p),np.zeros_like(self.parts['kick'])))
    def test_stereo_symmetry(self):
        s=np.repeat(self.parts['kick'][:,0,None],2,axis=1)
        parts={k:s.copy() for k in self.parts}
        d=linked_delta(parts,self.sr)
        self.assertLess(float(np.max(abs(d[:,0]-d[:,1]))),1e-14)
    def test_small_bounded_delta(self):
        d=linked_delta(self.parts,self.sr)
        ref=sum(self.parts.values())
        ratio=np.sqrt(np.mean(d**2)/np.mean(ref**2))
        self.assertLess(ratio,.09)
    def test_deterministic(self):
        a=linked_delta(self.parts,self.sr);b=linked_delta(self.parts,self.sr)
        np.testing.assert_array_equal(a,b)
    def test_rejects_unsafe(self):
        with self.assertRaises(ValueError):linked_delta(self.parts,self.sr,Profile(kick_body_db=4.0))
    def test_silence(self):
        p={k:np.zeros((22050,2)) for k in self.parts}
        self.assertTrue(np.array_equal(linked_delta(p,self.sr),np.zeros((22050,2))))
if __name__=='__main__': unittest.main()
