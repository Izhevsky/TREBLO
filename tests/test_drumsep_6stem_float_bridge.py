import unittest, tempfile, pathlib, sys, hashlib
import numpy as np
import soundfile as sf
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'tools'/'mastering'))
from drumsep_6stem_float_bridge import run,inspect_source,require_registry,sha256

class Faux:
    def __init__(self,raw,invalid=None): self.raw=raw;self.invalid=invalid
    def separate(self,samples,sample_rate,progress=False):
        assert sample_rate==44100
        return {k: (np.ones_like(samples)*q if self.invalid!=k else np.ones((1000,2),dtype='float32'))
                for k,q in [('kick',.12),('snare',.06),('toms',.03),('hh',.025),('ride',.02),('crash',.01)]}

class Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=pathlib.Path(self.temp.name);self.inp=self.path/'drums.wav'
        sf.write(self.inp,np.ones((2048,2),dtype='float32')*.245,44100,subtype='FLOAT')
        self.out=self.path/'out';self.cache=self.path/'cache'
    def test_dry_run_does_not_need_model(self):
        r=run(self.inp,self.out,self.cache,dry_run=True)
        self.assertEqual(r['status'],'DRY_RUN_NOT_INFERRED');self.assertFalse(self.out.exists())
    def test_neural_stub_float_export_and_manifest(self):
        sh=sha256(self.inp)
        r=run(self.inp,self.out,self.cache,engine_factory=lambda:Faux(None))
        self.assertTrue(r['inference_performed']);self.assertFalse(r['automatic_master_approved'])
        self.assertEqual(sha256(self.inp),sh)
        for k in r['output_stems']:
            file=self.out/'drums'/(k+'.wav')
            self.assertTrue(file.exists());self.assertEqual(sf.info(file).subtype,'FLOAT')
            self.assertEqual(sha256(file),r['stems_sha256'][k])
        a,_=sf.read(self.out/'drums/cymbals.wav')
        self.assertAlmostEqual(a[0,0],.03,places=5)
    def test_existing_target_forbidden(self):
        self.out.mkdir();(self.out/'drums').mkdir()
        with self.assertRaises(FileExistsError):run(self.inp,self.out,self.cache,engine_factory=lambda:Faux(None))
    def test_mismatched_stems_rejected_without_output(self):
        with self.assertRaises(ValueError):run(self.inp,self.out,self.cache,engine_factory=lambda:Faux(None,'hh'))
        self.assertFalse((self.out/'drums').exists())
    def test_reject_sr(self):
        sf.write(self.inp,np.zeros((2048,2)),48000)
        with self.assertRaises(ValueError):inspect_source(self.inp)
    def test_reject_mono(self):
        sf.write(self.inp,np.zeros(2048),44100)
        with self.assertRaises(ValueError):inspect_source(self.inp)
    def test_unknown_device(self):
        with self.assertRaises(ValueError):run(self.inp,self.out,self.cache,device='gpu:0',engine_factory=lambda:Faux(None))
    def test_no_implicit_download(self):
        with self.assertRaises((ImportError,FileNotFoundError,RuntimeError)):require_registry(self.cache,False)

if __name__=='__main__':unittest.main()