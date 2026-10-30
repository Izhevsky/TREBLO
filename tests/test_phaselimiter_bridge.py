"""CLI orchestration tests; fake engine is NOT a real DSP test."""
import importlib.util
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import wave

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("phase_bridge", ROOT / "tools/mastering/phaselimiter_bridge.py")
bridge = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = bridge
spec.loader.exec_module(bridge)

class BridgeTests(unittest.TestCase):
    def test_guards(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / "in.wav"
            p.touch()
            with self.assertRaises(bridge.MasteringError):
                bridge.Settings(p, p).validate()
            with self.assertRaises(bridge.MasteringError):
                bridge.Settings(p, Path(directory) / "out.flac", target_lufs=-3).validate()
            with self.assertRaises(bridge.MasteringError):
                bridge.Settings(p, Path(directory) / "out.wav").validate()

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "Requires ffmpeg")
    def test_mock_backend_roundtrip(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "orig.wav"
            with wave.open(str(source), "wb") as w:
                w.setnchannels(2); w.setsampwidth(2); w.setframerate(48000)
                w.writeframes(b"\x00\x00" * 2 * 96000)
            mock = root / "phase_limiter_mock"
            mock.write_text(
                "#!/usr/bin/env python3\n"
                "import sys,shutil\n"
                "flags=dict(x.split('=',1) for x in sys.argv[1:] if '=' in x)\n"
                "assert flags['--disable_input_encode']=='true'\n"
                "assert flags['--mastering']=='false'\n"
                "assert flags['--pre_compression']=='false'\n"
                "assert flags['--ceiling_mode']=='true_peak'\n"
                "shutil.copyfile(flags['--input'],flags['--output'])\n",
                encoding="utf8")
            mock.chmod(0o755)
            out = root / "master.flac"
            report = bridge.master(bridge.Settings(source, out, phase_limiter=str(mock)))
            self.assertEqual(report["native_rate_hz"], 44100)
            self.assertEqual(report["output_details"]["sample_rate"], 48000)
            self.assertEqual(report["input_sha256"], bridge.digest(source))
            self.assertTrue(out.is_file())
            self.assertTrue(out.with_suffix(".qc.json").is_file())

if __name__ == "__main__":
    unittest.main()
