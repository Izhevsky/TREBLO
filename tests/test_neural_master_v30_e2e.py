"""Synthetic end-to-end: guarded manifest -> actual FFmpeg limiter -> FLAC24/16.
No model weights or user audio. This tests integration, NOT neural quality.
"""
import hashlib, json, sys, tempfile, unittest
from pathlib import Path
import numpy as np
import soundfile as sf
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'/'mastering'))
from neural_master_v30 import render_guarded
from neural_provenance_gate import EXPECTED_WEIGHTS,EXPECTED_CONFIG,STEMS,digest

class EndToEnd(unittest.TestCase):
    def test_guarded_synthetic_master_and_dithered_flacs(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);d=p/'drums.wav';pr=p/'predicted';pr.mkdir();raw=p/'base_unlimited.wav'
            master=p/'previous.flac';studio=p/'studio.flac';out=p/'render'
            sr=44100;t=np.arange(sr)/sr
            rng=np.random.default_rng(123)
            parts={'kick':.085*np.sin(2*np.pi*75*t)*np.exp(-4*t),
              'snare':rng.normal(0,.006,len(t)), 'toms':.01*np.sin(2*np.pi*183*t),
              'hh':rng.normal(0,.005,len(t)), 'cymbals':.001*np.sin(2*np.pi*7200*t)}
            mix=sum(parts.values());pcm=np.column_stack([mix,.97*mix])
            sf.write(d,pcm,sr,subtype='PCM_16')
            sf.write(raw,pcm,sr,subtype='FLOAT')
            for f in (master,studio):sf.write(f,pcm,sr,subtype='PCM_24')
            stem_hashes={}
            for name,s in parts.items():
                z=pr/(name+'.wav');sf.write(z,np.column_stack([s,.97*s]),sr,subtype='FLOAT')
                stem_hashes[name]=digest(z)
            manifest={'inference_performed':True,'engine':'mdxnet_infer_mdx23c_6stem',
               'model':'drumsep-6stem','output_type':'actual_neural_predictions_float32_WAV',
               'output_stems':list(STEMS),'stems_sha256':stem_hashes,
               'weights_expected_sha256':EXPECTED_WEIGHTS,
               'model_config_expected_sha256':EXPECTED_CONFIG,
               'source_sha256':digest(d),'frames':sr,'sample_rate':sr,'channels':2}
            (pr/'INFERENCE_REPORT.json').write_text(json.dumps(manifest))
            source_hash=digest(d)
            result=render_guarded(d,pr,raw,master,studio,out,kick_db=.2,
                         target_lufs=-14,true_peak=-1.5,make_ab=False)
            self.assertEqual(result['candidate_status'],'EXPERIMENTAL_AWAITING_LISTENING')
            self.assertTrue((out/'PROVENANCE_QC.json').is_file())
            self.assertEqual(digest(d),source_hash)
            for bits in (24,16):
                f=out/f'Golden_Teeth_Neural_Kick_CANDIDATE_{bits}bit.flac'
                self.assertTrue(f.is_file())
                self.assertEqual(sf.info(f).frames,sr)
                self.assertEqual(sf.info(f).samplerate,sr)
            self.assertLessEqual(result['render']['master_loudnorm']['input_tp'],-1.45)

if __name__=='__main__':unittest.main()