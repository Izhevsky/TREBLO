import sys, unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'/'mastering'))
from drumsep_reference_benchmark import make_reference,score_sources,LABELS

class ReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.refs,cls.mix=make_reference(seconds=2.8)
    def test_deterministic(self):
        a,b=make_reference(seconds=2.8)
        np.testing.assert_array_equal(b,self.mix)
        for k in LABELS:np.testing.assert_array_equal(a[k],self.refs[k])
    def test_all_sources_active(self):
        for k in LABELS:self.assertGreater(np.max(abs(self.refs[k])),0,k)
    def test_exact_reference_is_high_sdr(self):
        q=score_sources(self.refs,self.refs,self.mix)
        self.assertLess(q['sum_reconstruction_error_db'],-100)
        for k in LABELS:self.assertGreater(q['measurements'][k]['si_sdr_db'],80)
    def test_leakage_is_measurable(self):
        bad={k:v.copy() for k,v in self.refs.items()}
        bad['snare']+=self.refs['hh']*0.8
        bad['hh']*=0.2
        q=score_sources(self.refs,bad,self.mix)
        self.assertLess(q['measurements']['snare']['si_sdr_db'],50)
        self.assertFalse(q['perceptual_quality_approved'])
    def test_reject_wrong_grid(self):
        bad=dict(self.refs);bad['kick']=bad['kick'][1:]
        with self.assertRaises(ValueError):score_sources(self.refs,bad,self.mix)
    def test_reject_nan(self):
        bad={k:v.copy() for k,v in self.refs.items()};bad['kick'][500,0]=np.nan
        with self.assertRaises(ValueError):score_sources(self.refs,bad,self.mix)
    def test_refuses_no_stems(self):
        with self.assertRaises(ValueError):score_sources(self.refs,{},self.mix)
    def test_reference_is_safe(self):
        self.assertTrue(np.max(abs(self.mix))<=0.8)
if __name__=='__main__':unittest.main()