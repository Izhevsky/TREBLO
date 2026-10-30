#!/usr/bin/env python3
"""Optional TREBLO phaselimiter final-mastering backend.

Requires official native phase_limiter, ffmpeg and ffprobe installed separately.
Never modifies the input. Do not feed it an already limited/mastered file.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass


class MasteringError(RuntimeError):
    pass


def execute(cmd: list[str], timeout: int = 1800) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=timeout)
    except FileNotFoundError as exc:
        raise MasteringError(f"Executable not found: {cmd[0]}") from exc
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise MasteringError(f"Command failed: {cmd[0]}: {getattr(exc, 'stderr', '')[-2000:]}") from exc


def binary(name: str) -> str:
    match = shutil.which(name)
    if not match:
        raise MasteringError(f"Install {name} or pass its full path.")
    return str(Path(match).resolve())


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def probe(path: Path, ffprobe: str) -> dict:
    data = json.loads(execute([
        ffprobe, "-v", "error", "-select_streams", "a:0",
        "-show_entries", "stream=sample_rate,channels,duration:format=duration",
        "-of", "json", str(path)
    ], timeout=120).stdout)
    streams = data.get("streams") or []
    if len(streams) != 1 or streams[0].get("channels") != 2:
        raise MasteringError("Only stereo audio is accepted.")
    rate = int(streams[0]["sample_rate"])
    if rate not in (44100, 48000, 88200, 96000):
        raise MasteringError(f"Unsupported input rate: {rate}")
    duration = float(streams[0].get("duration") or data.get("format", {}).get("duration") or 0)
    if duration <= 0 or not math.isfinite(duration):
        raise MasteringError("Invalid audio duration")
    return {"sample_rate": rate, "channels": 2, "duration_sec": duration}


def loudness(path: Path, ffmpeg: str) -> dict:
    # Analyze the actual final file; use input_* from this independent scan.
    err = execute([
        ffmpeg, "-hide_banner", "-nostdin", "-i", str(path), "-af",
        "loudnorm=I=-24:TP=-2:LRA=7:print_format=json", "-f", "null", "-"
    ], timeout=1200).stderr
    start = err.rfind("{\n")
    if start < 0:
        raise MasteringError("FFmpeg loudnorm JSON was not found")
    obj, _ = json.JSONDecoder().raw_decode(err[start:])
    return {k: float(obj[k]) for k in ("input_i", "input_tp", "input_lra", "input_thresh")}


@dataclass(frozen=True)
class Settings:
    source: Path
    output: Path
    target_lufs: float = -13.7
    ceiling_dbtp: float = -1.4
    phase_limiter: str = "phase_limiter"
    ffmpeg: str = "ffmpeg"
    ffprobe: str = "ffprobe"
    attempts: int = 3

    def validate(self) -> None:
        if not self.source.is_file():
            raise MasteringError(f"Source not found: {self.source}")
        if self.source.resolve() == self.output.resolve():
            raise MasteringError("Source and output cannot be identical")
        if self.output.suffix.lower() != ".flac":
            raise MasteringError("Final output must be FLAC")
        if not -28 <= self.target_lufs <= -7:
            raise MasteringError("target_lufs outside safety range")
        if not -5 <= self.ceiling_dbtp <= -0.5:
            raise MasteringError("ceiling_dbtp outside safety range")
        if not 1 <= self.attempts <= 5:
            raise MasteringError("attempts must be 1..5")


def master(cfg: Settings) -> dict:
    cfg.validate()
    native, ffmpeg, ffprobe = binary(cfg.phase_limiter), binary(cfg.ffmpeg), binary(cfg.ffprobe)
    original = cfg.source.resolve()
    output = cfg.output.resolve()
    input_hash = digest(original)
    input_info = probe(original, ffprobe)
    output.parent.mkdir(parents=True, exist_ok=True)
    history = []

    with tempfile.TemporaryDirectory(prefix="treblo-phase-") as td:
        tmp = Path(td)
        prepared = tmp / "in_44100_float.wav"
        # Native phaselimiter ALWAYS processes 44.1 kHz stereo.
        execute([ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
                 "-i", str(original), "-map", "0:a:0", "-ac", "2", "-ar", "44100",
                 "-c:a", "pcm_f32le", str(prepared)], timeout=1200)
        candidate = tmp / "final.flac"
        ceiling = cfg.ceiling_dbtp - 0.15
        for attempt in range(1, cfg.attempts + 1):
            native_wav = tmp / f"native_{attempt}.wav"
            native_tmp = tmp / f"native_tmp_{attempt}"
            native_tmp.mkdir()
            execute([native, f"--input={prepared}", f"--output={native_wav}",
                     f"--tmp={native_tmp}", f"--ffmpeg={ffmpeg}",
                     "--disable_input_encode=true", "--mastering=false",
                     "--pre_compression=false", "--mastering_reverb=false",
                     "--enhancement=false", "--freq_expansion=false",
                     "--low_cut_freq=0", "--high_cut_freq=0",
                     "--reference_mode=loudness", f"--reference={cfg.target_lufs}",
                     "--limiting_mode=phase", "--ceiling_mode=true_peak",
                     f"--ceiling={ceiling}", "--true_peak_oversample=4",
                     "--output_format=wav", "--bit_depth=32", "--sample_rate=44100"])
            if not native_wav.is_file() or native_wav.stat().st_size < 100:
                raise MasteringError("Native CLI did not produce audio")
            # SoXR to original sample rate, one TPDF pass on final float->PCM24.
            execute([ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
                     "-i", str(native_wav), "-af",
                     "aresample=resampler=soxr:precision=28:osf=s32:dither_method=triangular:output_sample_bits=24",
                     "-ar", str(input_info["sample_rate"]), "-ac", "2", "-c:a", "flac",
                     "-sample_fmt", "s32", "-bits_per_raw_sample", "24", str(candidate)], timeout=1200)
            output_info = probe(candidate, ffprobe)
            metrics = loudness(candidate, ffmpeg)
            overshoot = metrics["input_tp"] - cfg.ceiling_dbtp
            history.append({"pass": attempt, "native_ceiling": ceiling,
                            "final_tp": metrics["input_tp"]})
            if overshoot <= 0.05:
                break
            ceiling -= max(0.1, overshoot + 0.1)
        else:
            raise MasteringError(f"Final true peak still too high: {history}")

        if output_info["sample_rate"] != input_info["sample_rate"]:
            raise MasteringError("Output sample rate does not match source")
        if abs(output_info["duration_sec"] - input_info["duration_sec"]) > 0.025:
            raise MasteringError("Unexpected duration mismatch")
        if digest(original) != input_hash:
            raise MasteringError("Original source was modified")

        staging = output.with_name(output.name + ".partial")
        try:
            shutil.copyfile(candidate, staging)
            os.replace(staging, output)
        finally:
            staging.unlink(missing_ok=True)

    report = {
        "backend": "native_phase_limiter", "qc": "instrumental_only",
        "input": str(original), "input_sha256": input_hash,
        "output": str(output), "output_sha256": digest(output),
        "input_details": input_info, "output_details": output_info,
        "target_lufs": cfg.target_lufs, "ceiling_dbtp": cfg.ceiling_dbtp,
        "actual_loudnorm_input_metrics": metrics, "attempts": history,
        "native_rate_hz": 44100,
        "limitations": [
            "No restoration, EQ, or reverb was added by the adapter.",
            "48 kHz inputs are resampled 48->44.1->48 kHz: not bit-neutral.",
            "A real native phaselimiter run and listening QC are required.",
            "Local decoding does not prove a download link is accessible."
        ]
    }
    output.with_suffix(".qc.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--phase-limiter", default="phase_limiter")
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--ffprobe", default="ffprobe")
    parser.add_argument("--target-lufs", type=float, default=-13.7)
    parser.add_argument("--ceiling-dbtp", type=float, default=-1.4)
    parser.add_argument("--attempts", type=int, default=3)
    args = parser.parse_args(argv)
    try:
        result = master(Settings(source=args.source, output=args.output,
                                 target_lufs=args.target_lufs, ceiling_dbtp=args.ceiling_dbtp,
                                 phase_limiter=args.phase_limiter, ffmpeg=args.ffmpeg,
                                 ffprobe=args.ffprobe, attempts=args.attempts))
    except (MasteringError, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
