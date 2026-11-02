import tempfile,sys,json,hashlib,unittest
from pathlib import Path
import numpy as np
import soundfile as sf
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from neural_provenance_gate import check,digest,doctor,STEMS,EXPECTED_WEIGHTS,EXPECTED_CONFIG

class GateTests(unittest.TestCase):
 def setUp(self):
    self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
    self.base=Path(self.tmp.name);self.pred=self.base/'neural';self.pred.mkdir()
    sr=44100;n=sr
    rng=np.random.default_rng(2026)
    self.parts={
      'kick':(.1*np.sin(2*np.pi*72*np.arange(n)/sr)*np.exp(-np.arange(n)/sr*2)),
      'snare':rng.normal(size=n)*.008,
      'toms':np.sin(2*np.pi*160*np.arange(n)/sr)*.013,
      'hh':rng.normal(size=n)*.004,
      'cymbals':np.sin(2*np.pi*6000*np.arange(n)/sr)*.001,
    }
    mix=sum(self.parts.values())
    self.drums=self.base/'drums.wav'
    sf.write(self.drums,np.stack([mix,mix*.97],axis=-1),sr,subtype='PCM_16')
    self.stem_hashes={}
    for key,sig in self.parts.items():
      p=self.pred/(key+'.wav');sf.write(p,np.stack([sig,sig*.97],axis=-1),sr,subtype='FLOAT');self.stem_hashes[key]=digest(p)
    self.j={'inference_performed':True,'engine':'mdxnet_infer_mdx23c_6stem',
     'model':'drumsep-6stem','output_type':'actual_neural_predictions_float32_WAV',
     'output_stems':list(STEMS),'stems_sha256':self.stem_hashes,
     'weights_expected_sha256':EXPECTED_WEIGHTS,'model_config_expected_sha256':EXPECTED_CONFIG,
     'source_sha256':digest(self.drums),'frames':n,'sample_rate':sr,'channels':2}
    self.save()
 def save(self):
    (self.pred/'INFERENCE_REPORT.json').write_text(json.dumps(self.j),encoding='utf-8')
 def test_good_signed_manifest_qc(self):
    q=check(self.drums,self.pred)
    self.assertEqual(q['status'],'NEURAL_INPUTS_CHECKED_NOT_PERCEPTUALLY_APPROVED')
    self.assertLess(q['reconstruction_error_db'],-50)
    self.assertEqual(q['max_abs_lag_samples'],0)
 def test_no_model_inference_claim(self):
    self.j['inference_performed']=False;self.save()
    with self.assertRaisesRegex(ValueError,'provenance'):check(self.drums,self.pred)
 def test_wrong_model_hash(self):
    self.j['weights_expected_sha256']='x'*64;self.save()
    with self.assertRaisesRegex(ValueError,'checkpoint'):check(self.drums,self.pred)
 def test_wrong_source_hash(self):
    self.j['source_sha256']='a'*64;self.save()
    with self.assertRaisesRegex(ValueError,'different drums'):check(self.drums,self.pred)
 def test_missing_report(self):
    (self.pred/'INFERENCE_REPORT.json').unlink()
    with self.assertRaises(FileNotFoundError):check(self.drums,self.pred)
 def test_tampered_wav(self):
    with sf.SoundFile(self.pred/'kick.wav',mode='r+') as f:
      f.seek(1000);a=f.read(10,dtype='float32',always_2d=True);f.seek(1000);f.write(a*.5)
    with self.assertRaisesRegex(ValueError,'SHA-256 mismatch'):check(self.drums,self.pred)
 def test_incomplete_stem(self):
    (self.pred/'hh.wav').unlink()
    with self.assertRaises(FileNotFoundError):check(self.drums,self.pred)
 def test_reconstruction_failure_not_hash(self):
    with sf.SoundFile(self.pred/'kick.wav',mode='r+') as f:
      f.seek(0);f.write(np.zeros((f.frames,2),dtype='float32'))
    self.j['stems_sha256']['kick']=digest(self.pred/'kick.wav');self.save()
    with self.assertRaisesRegex(ValueError,'Reconstruction QC'):check(self.drums,self.pred)
 def test_nonfinite_audio_with_valid_hash(self):
    with sf.SoundFile(self.pred/'hh.wav',mode='r+') as f:
      f.seek(100);f.write(np.array([[float('nan'),float('nan')]],dtype='float32'))
    self.j['stems_sha256']['hh']=digest(self.pred/'hh.wav');self.save()
    with self.assertRaisesRegex(ValueError,'NaN or Inf'):check(self.drums,self.pred)
 def test_mismatched_samplerate(self):
    sf.write(self.pred/'hh.wav',np.zeros((44100,2)),48000,subtype='FLOAT')
    self.j['stems_sha256']['hh']=digest(self.pred/'hh.wav');self.save()
    with self.assertRaisesRegex(ValueError,'exact float32 grid'):check(self.drums,self.pred)
 def test_doctor_no_model(self):
    p=self.base/'unlimited.wav';sf.write(p,np.zeros((44100,2)),44100,subtype='FLOAT')
    q=doctor(self.drums,p,self.base/'missingcache')
    self.assertFalse(q['can_run_real_neural_inference_locally'])
    self.assertTrue(q['unlimited_float_present'])
 def test_reject_wrong_stem_encoding(self):
    p=self.pred/'cymbals.wav';sig=np.zeros((44100,2));sf.write(p,sig,44100,subtype='PCM_24')
    self.j['stems_sha256']['cymbals']=digest(p);self.save()
    with self.assertRaisesRegex(ValueError,'exact float32 grid'):check(self.drums,self.pred)

if __name__=='__main__': unittest.main()