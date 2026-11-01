"""Independent unit tests for band mono cancellation checker."""
import sys,tempfile,unittest
from pathlib import Path
import numpy as np
import soundfile as sf
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'/'mastering'))
from codec_mono_qc import inspect_windows,run

class TestCodecMono(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.rate=44100
        t=np.arange(self.rate*2)/self.rate
        self.t=t
    def write(self,x):
        p=self.root/'x.wav';sf.write(p,x,self.rate,subtype='FLOAT');return p
    def test_identical_channels_no_mono_loss(self):
        x=.2*np.sin(2*np.pi*800*self.t)
        r=inspect_windows(self.write(np.column_stack([x,x])),starts=[0],seconds=1)[0]
        b=next(b for b in r['bands'] if b['hz']=='500-4000')
        self.assertAlmostEqual(b['mono_loss_db'],0.0,places=2)
        self.assertFalse(b['warning'])
    def test_antiphase_detected(self):
        x=.2*np.sin(2*np.pi*800*self.t)
        r=inspect_windows(self.write(np.column_stack([x,-x])),starts=[0],seconds=1)[0]
        b=next(b for b in r['bands'] if b['hz']=='500-4000')
        self.assertLess(b['mono_loss_db'],-20)
        self.assertTrue(b['warning'])
    def test_inactive_band_not_flagged(self):
        x=.2*np.sin(2*np.pi*70*self.t)
        r=inspect_windows(self.write(np.column_stack([x,-x])),starts=[0],seconds=1)[0]
        b=next(b for b in r['bands'] if b['hz']=='4000-15000')
        self.assertFalse(b['warning'])
    def test_original_hash_unchanged(self):
        x=.15*np.sin(2*np.pi*90*self.t)
        p=self.write(np.column_stack([x,x]));h=p.read_bytes()
        r=run(p,self.root/'report.json',starts=[0]);self.assertEqual(h,p.read_bytes())
        self.assertTrue((self.root/'report.json').is_file());self.assertFalse(r['warnings'])
if __name__=='__main__':unittest.main()