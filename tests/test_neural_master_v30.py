import unittest,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from neural_master_v30 import render_guarded
class SafetyTests(unittest.TestCase):
 def test_reject_large_gain_before_any_fs(self):
  with tempfile.TemporaryDirectory() as td:
   wd=Path(td)/'new';
   with self.assertRaisesRegex(ValueError,'kick_db'):
    render_guarded(Path('x'),Path('y'),Path('z'),Path('a'),Path('b'),wd,kick_db=.8)
   self.assertFalse(wd.exists())
 def test_missing_provenance_never_starts_mastering(self):
  with tempfile.TemporaryDirectory() as td:
   wd=Path(td)/'new'
   with self.assertRaises(FileNotFoundError):
    render_guarded(Path(td)/'missing.wav',Path(td)/'not-generated',Path(td)/'raw.wav',Path(td)/'m.flac',Path(td)/'studio.flac',wd)
   self.assertFalse(wd.exists())
 def test_reject_workdir_reuse(self):
  with tempfile.TemporaryDirectory() as td:
   with self.assertRaises(FileExistsError):
    render_guarded(Path('x'),Path('y'),Path('z'),Path('a'),Path('b'),Path(td))
if __name__=='__main__':unittest.main()