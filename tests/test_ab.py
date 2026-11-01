import sys, tempfile, unittest
from pathlib import Path
import numpy as np
import soundfile as sf
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.mastering.make_ab import create_ab
class TestAB(unittest.TestCase):
    def test_ab_frames_and_constant_gain(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d); sr=44100
            t=np.arange(2*sr*3,dtype=np.float32)/sr
            w=(.05*np.sin(2*np.pi*180*t)).astype('float32')
            stereo=np.column_stack([w,w])
            a,b,o=d/'a.wav',d/'b.wav',d/'ab.flac'
            sf.write(a,stereo,sr,subtype='FLOAT');sf.write(b,stereo*.6,sr,subtype='FLOAT')
            meta=create_ab(a,b,o,[0.5],seconds=2.)
            self.assertEqual(meta['comparison'],'KNOWN_A_THEN_B')
            with sf.SoundFile(o) as f:
                self.assertEqual(len(f),int(sr*(2+0.75+2+0.75)))
                self.assertEqual(f.subtype,'PCM_24')
if __name__=='__main__':unittest.main()