import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'/'mastering'))
import tempfile, unittest
import numpy as np
import soundfile as sf
from drumsep_real_smoke import synthetic_drums,inspect_result

class Tests(unittest.TestCase):
    def test_generates_non_silent_original_audio(self):
        a=synthetic_drums()
        self.assertEqual(a.shape,(88200,2))
        self.assertTrue(np.isfinite(a).all())
        self.assertTrue((a*a).mean()>1e-7)
    def test_invalid_time_rejected(self):
        with self.assertRaises(ValueError):synthetic_drums(seconds=20)
    def test_no_output_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            t=Path(td);src=t/'synthetic.wav'
            sf.write(src,synthetic_drums(),44100,subtype='FLOAT')
            with self.assertRaises(RuntimeError):inspect_result(src,t)
    def test_real_output_gate_valid_and_reconstruction(self):
        with tempfile.TemporaryDirectory() as td:
            t=Path(td);src=t/'synthetic.wav'
            x=synthetic_drums()
            sf.write(src,x,44100,subtype='FLOAT')
            o=t/src.stem;o.mkdir()
            for stem,v in [('kick',0.8),('snare',0.05),('toms',0.04),('hh',0.06),('cymbals',0.05)]:
                sf.write(o/(stem+'.wav'),x*v,44100,subtype='FLOAT')
            q=inspect_result(src,t)
            self.assertLess(q['sum_reconstruction_error_db'],-100)
            self.assertEqual(len(q['stem_sha256']),5)
if __name__=='__main__':unittest.main()