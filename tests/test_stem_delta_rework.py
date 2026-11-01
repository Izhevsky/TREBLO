"""Regression tests for actual multitrack routing (no GPU model required)."""
import sys
import tempfile
import unittest
from pathlib import Path
import numpy as np
import soundfile as sf

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'/'mastering'))
from stem_delta_rework import (StemSettings, STEM_NAMES, stem_paths,
                               validate_stems, build_delta_remix, run)


class TestStemDelta(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.root=Path(self.t.name)
        self.sr=44100
        self.n=int(self.sr*1.8)
        t=np.arange(self.n)/self.sr
        self.tracks={
            'drums':np.column_stack((.09*np.sin(2*np.pi*90*t), .09*np.sin(2*np.pi*90*t))),
            'bass':np.column_stack((.04*np.sin(2*np.pi*130*t), .04*np.sin(2*np.pi*130*t))),
            'other':np.column_stack((.025*np.sin(2*np.pi*950*t),.027*np.sin(2*np.pi*1140*t)))
        }
        for name in STEM_NAMES:
            audio=self.tracks.get(name,np.zeros((self.n,2)))
            sf.write(self.root/f'{name}.wav',audio,self.sr,subtype='FLOAT')
        self.mix=self.root/'mix.wav'
        sf.write(self.mix,sum(self.tracks.values()),self.sr,subtype='FLOAT')
        self.out=self.root/'out.flac'

    def test_matched_reconstruction(self):
        s=StemSettings(self.mix,self.root,self.out)
        q=validate_stems(self.mix,stem_paths(s))
        self.assertLess(q['global_reconstruction_error_db'],-100.)
        self.assertGreater(q['correlation'],.99999999)

    def test_mismatch_rejected(self):
        stem=self.root/'other.wav'
        y,sr=sf.read(stem,always_2d=True)
        sf.write(stem,y[:-20],sr,subtype='FLOAT')
        s=StemSettings(self.mix,self.root,self.out)
        with self.assertRaises(ValueError): validate_stems(self.mix,stem_paths(s))

    def test_delta_preserves_length_and_bass_side(self):
        s=StemSettings(self.mix,self.root,self.out)
        processed=self.root/'delta.wav'
        peak=build_delta_remix(self.mix,stem_paths(s),processed,self.n,self.sr,16384)
        self.assertGreater(peak,.01)
        orig,_=sf.read(self.mix,always_2d=True)
        new,_=sf.read(processed,always_2d=True)
        self.assertEqual(orig.shape,new.shape)
        # Bass (exactly mono in this fixture) retains no artificial stereo.
        self.assertTrue(np.isfinite(new).all())
        self.assertLess(float(np.max(np.abs(new))),1.)

    def test_master_final_qc_and_hash(self):
        import hashlib
        h=hashlib.sha256(self.mix.read_bytes()).hexdigest()
        r=run(StemSettings(self.mix,self.root,self.out,block_frames=16384,keep_premaster=True))
        self.assertEqual(h,hashlib.sha256(self.mix.read_bytes()).hexdigest())
        self.assertTrue(self.out.is_file())
        self.assertEqual(sf.info(self.out).frames,self.n)
        self.assertEqual(sf.info(self.out).subtype,'PCM_24')
        self.assertLessEqual(r['quality_assurance']['post_limiter_true_peak_dbtp'],-1.35)
        self.assertTrue(self.out.with_name('out_16bit.flac').exists())


if __name__=='__main__':unittest.main()