from __future__ import annotations
import math
from pathlib import Path
import sys
import tempfile
import unittest
import numpy as np
import soundfile as sf
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'/'mastering'))
from neural_drumsep_bridge import (model_command,render_delta,apply_delta,QC,
                                check_model_metadata, expected_sources, STEMS)

class BackendTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        sr=44100;n=11025
        t=np.arange(n)/sr
        signal=np.zeros((n,2),dtype=np.float32)
        rng=np.random.default_rng(321)
        self.parts={}
        for i,k in enumerate(STEMS):
            f=(43,160,290,6500,9500)[i]
            x=(.12 / (i+1))*np.sin(2*np.pi*f*t)
            x=np.column_stack((x,x*.98)).astype('float32')
            self.parts[k]=x
            signal+=x
        self.mix=self.root/'drums.wav';sf.write(self.mix,signal,sr,subtype='FLOAT')
        self.stems={}
        for k,v in self.parts.items():
            p=self.root/f'{k}.wav';sf.write(p,v,sr,subtype='FLOAT');self.stems[k]=p
        self.output=self.root/'delta.wav';self.report=self.root/'report.json'
    def tearDown(self): self.temp.cleanup()
    def test_qc_safe_delta(self):
        original=self.mix.read_bytes()
        result=render_delta(self.mix,self.stems,self.output,self.report)
        self.assertEqual(result['qc_status'],'PASS')
        self.assertEqual(result['frames'],11025)
        self.assertLess(result['sum_reconstruction_error_db'],-90)
        self.assertLess(result['delta_relative_rms_db'],-20)
        self.assertEqual(self.mix.read_bytes(),original)
    def test_noop_preserves_grid(self):
        gains={k:0.0 for k in STEMS}
        result=render_delta(self.mix,self.stems,self.output,self.report,changes=gains)
        delta,_=sf.read(self.output)
        self.assertTrue(np.all(delta==0))
        self.assertLess(result['delta_relative_rms_db'],-200)
    def test_rejects_stem_grid_mismatch(self):
        sf.write(self.stems['hh'],np.zeros((10000,2)),44100)
        with self.assertRaises(ValueError):render_delta(self.mix,self.stems,self.output,self.report)
    def test_rejects_nonfinite_gain(self):
        gains={k:0.0 for k in STEMS};gains['hh']=float('nan')
        with self.assertRaises(ValueError):render_delta(self.mix,self.stems,self.output,self.report,changes=gains)
    def test_rejects_bad_reconstruction(self):
        sf.write(self.stems['kick'],np.zeros((11025,2)),44100)
        with self.assertRaises(RuntimeError):render_delta(self.mix,self.stems,self.output,self.report)
        self.assertFalse(self.output.exists())
    def test_rejects_large_delta(self):
        gains={k:1.2 for k in STEMS}
        with self.assertRaises(RuntimeError):render_delta(self.mix,self.stems,self.output,self.report,changes=gains,qc=QC(max_delta_db=-30.0))
        self.assertFalse(self.output.exists())
    def test_unchanged_drums_with_mix(self):
        render_delta(self.mix,self.stems,self.output,self.report)
        self.assertTrue(apply_delta(self.mix,self.output,self.root/'unlimited.wav')['not_mastered'])
        o,_=sf.read(self.root/'unlimited.wav')
        a,_=sf.read(self.mix);d,_=sf.read(self.output)
        self.assertLess(float(np.max(abs(o-a-d))),1e-7)
    def test_malformed_backend_model_file(self):
        cfg=self.root/'model.yaml';cfg.write_text('model_type: mdx23c')
        ckpt=self.root/'model.ckpt';ckpt.write_bytes(b'abcd')
        with self.assertRaises(ValueError):check_model_metadata(cfg,ckpt)
    def test_inference_command_real_cli(self):
        repo=self.root/'MSST';repo.mkdir()
        entry=repo/'inference.py';entry.write_text('# placeholder for argv verification')
        cfg=self.root/'model.yaml';cfg.write_text('dummy')
        cp=self.root/'model.ckpt';cp.write_bytes(b'0'*5000)
        ind=self.root/'in';ind.mkdir()
        cmd=model_command(repo,cfg,cp,ind,self.root/'out',cpu=True)
        self.assertEqual(cmd[1],str(entry.resolve()))
        self.assertIn('--force_cpu',cmd)
        self.assertIn('--pcm_type',cmd)
        self.assertNotIn('msst',cmd[:2])
    def test_outputs_must_exist(self):
        with self.assertRaises(FileNotFoundError):expected_sources(self.root)
    def test_no_overwrite(self):
        with self.assertRaises(ValueError):render_delta(self.mix,self.stems,self.mix,self.report)
    def test_original_does_not_get_overwritten(self):
        render_delta(self.mix,self.stems,self.output,self.report)
        with self.assertRaises(ValueError):apply_delta(self.mix,self.output,self.mix)

if __name__=='__main__':unittest.main()