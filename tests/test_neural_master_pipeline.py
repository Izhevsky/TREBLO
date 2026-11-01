import sys, tempfile, unittest
from pathlib import Path
import numpy as np
import soundfile as sf
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'/'mastering'))
from neural_master_pipeline import (source_preflight,normalize_float_premaster,render)

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.d=Path(self.tmp.name)
        sr=44100; frames=sr*3
        t=np.arange(frames,dtype=np.float64)/sr
        kick=.055*np.sin(2*np.pi*62*t)*np.exp(-4*(t%0.5))
        hh=.006*np.random.default_rng(42).normal(size=frames)
        sn=.006*np.random.default_rng(43).normal(size=frames)
        tom=.005*np.sin(2*np.pi*220*t)
        cym=.003*np.sin(2*np.pi*5500*t)
        parts={'kick':kick,'hh':hh,'snare':sn,'toms':tom,'cymbals':cym}
        self.stems=self.d/'neural';self.stems.mkdir()
        for k,x in parts.items():sf.write(self.stems/f'{k}.wav',np.column_stack([x,x*.99]),sr,subtype='FLOAT')
        self.drums=self.d/'drums.wav';self.unlimited=self.d/'raw.wav'
        self.ref=self.d/'ref.flac';self.favourite=self.d/'favourite.flac'
        y=sum(parts.values());z=np.column_stack([y,y*.99]);
        sf.write(self.drums,z,sr,subtype='PCM_16')
        sf.write(self.unlimited,z,sr,subtype='FLOAT')
        sf.write(self.ref,z,sr,subtype='PCM_24');sf.write(self.favourite,z,sr,subtype='PCM_24')

    def tearDown(self):self.tmp.cleanup()

    def test_preflight_valid(self):
        r=source_preflight(self.drums,self.unlimited,self.ref,self.favourite)
        self.assertEqual(r['frames'],132300)
        self.assertEqual(len(r['source_sha256']),4)

    def test_preflight_reject_grid_mismatch(self):
        wrong=self.d/'wrong.wav';sf.write(wrong,np.zeros((44100,2)),44100,subtype='FLOAT')
        with self.assertRaises(ValueError):source_preflight(self.drums,wrong,self.ref,self.favourite)

    def test_preflight_reject_master_as_unlimited(self):
        with self.assertRaises(ValueError):source_preflight(self.drums,self.ref,self.ref,self.favourite)

    def test_normalize_preserves_frames_and_peak(self):
        pre=self.d/'pre.wav';q=normalize_float_premaster(self.unlimited,pre)
        self.assertEqual(sf.info(pre).frames,sf.info(self.unlimited).frames)
        with sf.SoundFile(pre) as f: data=f.read(dtype='float64')
        self.assertAlmostEqual(float(np.max(abs(data))),10**(-6/20),places=5)
        self.assertAlmostEqual(q['target_sample_peak_dbfs'],-6)

    def test_normalize_refuses_overwrite(self):
        with self.assertRaises(ValueError):normalize_float_premaster(self.unlimited,self.unlimited)

    def test_render_refuses_missing_model(self):
        (self.stems/'kick.wav').unlink()
        with self.assertRaises(FileNotFoundError):render(self.drums,self.unlimited,self.ref,self.favourite,self.stems,self.d/'output',make_ab=False)
        self.assertFalse((self.d/'output').exists())

    def test_render_refuses_untrusted_gain(self):
        with self.assertRaises(ValueError):render(self.drums,self.unlimited,self.ref,self.favourite,self.stems,self.d/'output',kick_db=1.0,make_ab=False)

    def test_end_to_end_synthetic_master_without_model_download(self):
        # Tests the REAL signal/limiter/FLAC pipeline with synthetic predicted
        # stems. It does NOT claim to have run neural inference.
        out=self.d/'result'
        r=render(self.drums,self.unlimited,self.ref,self.favourite,self.stems,out,
                 kick_db=.20,target_lufs=-14.0,true_peak=-1.5,make_ab=False)
        self.assertTrue((out/'Golden_Teeth_Neural_Kick_CANDIDATE_24bit.flac').is_file())
        self.assertEqual(sf.info(out/'Golden_Teeth_Neural_Kick_CANDIDATE_24bit.flac').frames,132300)
        self.assertLessEqual(r['master_loudnorm']['input_tp'],-1.45)
        self.assertEqual(r['subjective_qc'],'AWAITING_LISTENER')
        with self.assertRaises(FileExistsError):render(self.drums,self.unlimited,self.ref,self.favourite,self.stems,out,make_ab=False)

if __name__=='__main__':unittest.main()