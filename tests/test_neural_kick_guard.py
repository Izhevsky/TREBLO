import unittest,tempfile,sys
from pathlib import Path
import numpy as np
import soundfile as sf
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/mastering'))
from neural_kick_guard import build_candidate
from neural_drumsep_bridge import STEMS

class GuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.dir=self.root/'pred';self.dir.mkdir()
        self.n=12000;self.sr=44100
        t=np.arange(self.n)/self.sr
        self.parts={k:np.column_stack((.11/(i+1)*np.sin(2*np.pi*(50+i*210)*t),
                                  .11/(i+1)*np.sin(2*np.pi*(50+i*210)*t))) for i,k in enumerate(STEMS)}
        self.drums=self.root/'drums.wav';self.baseline=self.root/'baseline.wav'
        mix=sum(self.parts.values())
        sf.write(self.drums,mix,self.sr,subtype='FLOAT')
        sf.write(self.baseline,mix,self.sr,subtype='FLOAT')
        for k,v in self.parts.items():sf.write(self.dir/f'{k}.wav',v,self.sr,subtype='FLOAT')
    def tearDown(self):self.tmp.cleanup()
    def test_candidate_good(self):
        old=self.drums.read_bytes()
        q=build_candidate(self.drums,self.baseline,self.dir,self.root/'w')
        self.assertEqual(q['qc_status'],'PASS')
        self.assertEqual(q['gain_db']['hh'],0)
        self.assertTrue(q['human_listening_required'])
        self.assertEqual(self.drums.read_bytes(),old)
        self.assertTrue((self.root/'w'/'neural_kick_candidate_UNMASTERED_float32.wav').exists())
    def test_no_gain_is_identity(self):
        build_candidate(self.drums,self.baseline,self.dir,self.root/'w',kick_db=0)
        z,_=sf.read(self.root/'w'/'neural_kick_candidate_UNMASTERED_float32.wav')
        x,_=sf.read(self.baseline)
        np.testing.assert_allclose(z,x,atol=1e-7)
    def test_unsafe_gain_rejected(self):
        for v in (-.1,.36):
            with self.assertRaises(ValueError):build_candidate(self.drums,self.baseline,self.dir,self.root/'w',kick_db=v)
    def test_no_overwrite(self):
        build_candidate(self.drums,self.baseline,self.dir,self.root/'w')
        with self.assertRaises(FileExistsError):build_candidate(self.drums,self.baseline,self.dir,self.root/'w')
    def test_bad_neural_sum_rejected(self):
        sf.write(self.dir/'hh.wav',self.parts['hh']*30,self.sr,subtype='FLOAT')
        with self.assertRaises(RuntimeError):build_candidate(self.drums,self.baseline,self.dir,self.root/'w')
        self.assertFalse((self.root/'w'/'neural_kick_candidate_UNMASTERED_float32.wav').exists())
    def test_wrong_grid_rejected(self):
        sf.write(self.dir/'kick.wav',self.parts['kick'][:-5],self.sr,subtype='FLOAT')
        with self.assertRaises(ValueError):build_candidate(self.drums,self.baseline,self.dir,self.root/'w')
if __name__=='__main__':unittest.main()