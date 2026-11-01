"""Fast CPU tests; no neural checkpoint or third-party VST required."""
import sys
import tempfile
from pathlib import Path
import unittest
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.mastering.astra_pedalboard import Config, run, sample_count, sha256
from tools.mastering.msst_bridge import validate_reconstruction, separation_command

class TestAstra(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        rate = 44100
        n = int(rate*2.7)
        t = np.arange(n)/rate
        left = .075*np.sin(2*np.pi*80*t) + .04*np.sin(2*np.pi*220*t)
        right = .07*np.sin(2*np.pi*80*t) + .04*np.sin(2*np.pi*380*t)
        self.source = self.root / 'source.wav'
        sf.write(self.source, np.column_stack((left,right)),rate,subtype='FLOAT')
        self.out=self.root/'output.flac'

    def test_dry_run_does_not_write(self):
        h=sha256(self.source)
        result=run(Config(self.source,self.out,dry_run=True))
        self.assertEqual(result['status'],'DRY_RUN')
        self.assertEqual(h,sha256(self.source))
        self.assertFalse(self.out.exists())

    def test_reject_source_overwrite(self):
        with self.assertRaises(ValueError):
            run(Config(self.source,self.source))

    def test_run_audio_export_and_qc(self):
        fingerprint=sha256(self.source)
        report=run(Config(self.source,self.out,lowmid_db=-0.2,presence_db=0.3,air_db=0.0,keep_premaster=True))
        self.assertEqual(sample_count(self.source),sample_count(self.out))
        self.assertEqual(fingerprint,sha256(self.source))
        self.assertLessEqual(report['final_loudnorm']['input_tp'],-1.35)
        self.assertTrue(self.out.with_suffix('.qc.json').exists())
        self.assertTrue(self.out.with_name('output_16bit.flac').exists())
        premaster=self.out.with_name('output_PREMASTER_float32.wav')
        self.assertTrue(premaster.exists())
        with sf.SoundFile(premaster) as f:
            self.assertEqual(f.subtype,'FLOAT')
        self.assertEqual(report['native_phaselimiter'],'NOT_USED')

    def test_msst_reconstruction_and_bad_stems(self):
        x,sr=sf.read(self.source,dtype='float32',always_2d=True)
        a,b=self.root/'bass.wav',self.root/'other.wav'
        sf.write(a,x*0.4,sr,subtype='FLOAT')
        sf.write(b,x*0.6,sr,subtype='FLOAT')
        r=validate_reconstruction(self.source,[a,b])
        self.assertEqual(r['status'],'PASS')
        self.assertFalse(r['automatic_remix_approved'])
        sf.write(b,x[:-1],sr,subtype='FLOAT')
        with self.assertRaises(ValueError):
            validate_reconstruction(self.source,[a,b])

    def test_msst_require_model_files(self):
        with self.assertRaises(FileNotFoundError):
            separation_command(model_type='bs_roformer',config=self.root/'no.yaml',
              checkpoint=self.root/'no.ckpt',input_folder=self.root,output_folder=self.root/'stems')

if __name__=='__main__':unittest.main()