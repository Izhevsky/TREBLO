#!/usr/bin/env python3
"""TREBLO / Astra v2: reproducible Pedalboard -> float32 premaster -> mastering.

Optional VST3 effects, conservative default EQ, independent final-file QC.
Requires pedalboard, numpy, scipy, soundfile and ffmpeg with SoXR.
No automatic source separation or perceptual quality claims.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, asdict
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

import numpy as np
import soundfile as sf


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def shell(args: list[str], timeout: int = 1200) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, check=True, timeout=timeout)
    except FileNotFoundError as exc:
        raise RuntimeError(f"Missing executable: {args[0]}") from exc
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as exc:
        raise RuntimeError(f"External command failed: {args[0]} — {str(getattr(exc, 'stderr', ''))[-1200:]}") from exc


def scan_loudness(path: Path, ffmpeg: str) -> dict[str, float]:
    txt = shell([ffmpeg, "-hide_banner", "-nostdin", "-i", str(path), "-af",
                 "loudnorm=I=-24:TP=-2:LRA=7:print_format=json", "-f", "null", "-"], 900).stderr
    ix = txt.rfind('{\n')
    if ix == -1:
        raise RuntimeError("Missing loudnorm JSON")
    data, _ = json.JSONDecoder().raw_decode(txt[ix:])
    return {k: float(data[k]) for k in ("input_i", "input_tp", "input_lra", "input_thresh")}


def independently_scan_ebur128(path: Path, ffmpeg: str) -> str:
    import re
    txt = shell([ffmpeg, "-hide_banner", "-nostdin", "-i", str(path), "-filter_complex",
                 "ebur128=peak=true", "-f", "null", "-"], 900).stderr
    # final summary near end
    tail = txt[txt.rfind('Summary:'):]
    match = re.search(r'Integrated loudness:\s*I:\s*([-+0-9.]+) LUFS', tail)
    return match.group(1) if match else "not_parsed"


@dataclass(frozen=True)
class Config:
    input: Path
    output: Path
    target_lufs: float = -13.7
    true_peak_ceiling: float = -1.4
    # Each small tonal move is explicitly optional. 0 is neutral.
    lowmid_db: float = -0.35
    presence_db: float = 0.2
    air_db: float = 0.3
    vst3_paths: tuple[str, ...] = ()
    block_frames: int = 32768
    ffmpeg: str = 'ffmpeg'
    compatible_16bit: bool = True
    keep_premaster: bool = False
    dry_run: bool = False

    def validate(self) -> None:
        if not self.input.is_file():
            raise ValueError("Input file does not exist")
        if self.input.resolve() == self.output.resolve():
            raise ValueError("Cannot overwrite input")
        if self.output.suffix.lower() != '.flac':
            raise ValueError("Output must end in .flac")
        if not -25 <= self.target_lufs <= -7:
            raise ValueError("Target LUFS outside safety range")
        if not -4 <= self.true_peak_ceiling <= -0.5:
            raise ValueError("Ceiling outside safety range")
        if self.block_frames < 4096:
            raise ValueError("Block size too small")
        for value in (self.lowmid_db, self.presence_db, self.air_db):
            if not math.isfinite(value) or abs(value) > 3:
                raise ValueError("EQ gains must be finite and <= 3 dB")
        for p in self.vst3_paths:
            if not Path(p).exists():
                raise ValueError(f"VST3 path does not exist: {p}")


def make_board(cfg: Config):
    # Import is delayed so CLI --help / dry-run can work without Pedalboard installed.
    from pedalboard import Pedalboard, PeakFilter, HighShelfFilter, load_plugin
    effects = []
    if cfg.lowmid_db:
        effects.append(PeakFilter(cutoff_frequency_hz=360.0, gain_db=cfg.lowmid_db, q=0.85))
    if cfg.presence_db:
        effects.append(PeakFilter(cutoff_frequency_hz=3000.0, gain_db=cfg.presence_db, q=0.9))
    if cfg.air_db:
        effects.append(HighShelfFilter(cutoff_frequency_hz=9000.0, gain_db=cfg.air_db, q=0.7))
    for path in cfg.vst3_paths:
        effects.append(load_plugin(str(Path(path).resolve())))
    return Pedalboard(effects)


def sample_count(path: Path) -> tuple[int, int, int]:
    with sf.SoundFile(path) as f:
        return (len(f), f.samplerate, f.channels)


def render_premaster(cfg: Config, tmp: Path) -> tuple[Path, dict]:
    board = make_board(cfg)
    raw = tmp / 'processed_float32.wav'
    nframes, rate, channels = sample_count(cfg.input)
    if channels != 2 or rate not in (44100,48000,88200,96000) or nframes == 0:
        raise ValueError("Require non-empty stereo WAV/FLAC at 44.1/48/88.2/96 kHz")
    peak = 0.0
    rendered = 0
    with sf.SoundFile(cfg.input) as source, sf.SoundFile(raw, 'w', samplerate=rate,
                                                         channels=2, subtype='FLOAT', format='WAV') as output:
        first = True
        while True:
            frame = source.read(cfg.block_frames, dtype='float32', always_2d=True)
            if len(frame) == 0:
                break
            if not np.isfinite(frame).all():
                raise RuntimeError('Input contains NaN/Inf')
            processed = np.asarray(board(frame.T.copy(), rate, reset=first)).T
            first = False
            if processed.shape != frame.shape or not np.isfinite(processed).all():
                raise RuntimeError('Plugin changed frame count or produced invalid samples')
            peak = max(peak, float(np.max(np.abs(processed))))
            output.write(processed)
            rendered += len(processed)
    if peak < 1e-10 or rendered != nframes:
        raise RuntimeError('Silent input or altered frame count')
    gain = 10 ** (-6.0 / 20) / peak
    premaster = tmp / 'PREMASTER_float32.wav'
    with sf.SoundFile(raw) as source, sf.SoundFile(premaster, 'w', samplerate=rate,
                                                  channels=2, subtype='FLOAT', format='WAV') as output:
        while True:
            block = source.read(cfg.block_frames, dtype='float32', always_2d=True)
            if not len(block):
                break
            output.write((block.astype(np.float64) * gain).astype(np.float32))
    return premaster, {"frames": nframes, "sample_rate": rate, "pre_norm_peak": peak,
                       "constant_gain_db": 20*math.log10(gain), "sample_peak_dbfs": -6.0,
                       "plugins": [str(x) for x in board]}


def convert_float_to_pcm(float_master: Path, output: Path, ffmpeg: str, bits: int):
    output.parent.mkdir(parents=True, exist_ok=True)
    # 16-bit and 24-bit are separately quantized from SAME float master, once each.
    # For 24-bit: FFmpeg uses signed s32 container with 24 valid bits.
    fmt = 's16' if bits == 16 else 's32'
    extra = [] if bits == 16 else ["-bits_per_raw_sample", "24"]
    shell([ffmpeg, '-v', 'error', '-nostdin', '-y', '-i', str(float_master),
           '-af', f'aresample=osf={fmt}:dither_method=triangular:output_sample_bits={bits}',
           '-c:a', 'flac', '-sample_fmt', fmt, *extra, str(output)], 1000)


def master_premaster(premaster: Path, out_float: Path, cfg: Config,
                     premaster_lufs: float, ceiling: float) -> None:
    frames, sample_rate, _ = sample_count(premaster)
    ratio = 4
    ceiling_lin = 10 ** (ceiling/20)
    gain_db = cfg.target_lufs - premaster_lufs
    shell([cfg.ffmpeg, '-v', 'error', '-nostdin', '-y', '-i', str(premaster),
           '-af', f'aresample={sample_rate*ratio}:resampler=soxr:precision=28,'
                  f'volume={gain_db:.7f}dB,'
                  f'alimiter=limit={ceiling_lin:.9f}:attack=5:release=90:level=0:latency=1,'
                  f'aresample={sample_rate}:resampler=soxr:precision=28',
           '-ac', '2', '-c:a', 'pcm_f32le', str(out_float)], 1200)
    if sample_count(out_float) != (frames, sample_rate, 2):
        raise RuntimeError('Unexpected resampler/limiter frame count')


def run(cfg: Config) -> dict:
    cfg.validate()
    fingerprint = sha256(cfg.input)
    source_info = sample_count(cfg.input)
    if cfg.dry_run:
        return {"status": "DRY_RUN", "source": str(cfg.input), "hash": fingerprint,
                "format": source_info, "target_lufs": cfg.target_lufs,
                "ceiling_dbtp": cfg.true_peak_ceiling,
                "vst3_paths": cfg.vst3_paths, "tonal_eq_db": [cfg.lowmid_db, cfg.presence_db, cfg.air_db]}
    if not shutil.which(cfg.ffmpeg):
        raise RuntimeError(f'FFmpeg missing: {cfg.ffmpeg}')
    cfg.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='treblo-astra-') as work:
        tmp = Path(work)
        premaster, notes = render_premaster(cfg, tmp)
        pre_qc = scan_loudness(premaster, cfg.ffmpeg)
        result_flac = tmp / 'result24.flac'
        attempts=[]
        for attempt in range(3):
            ceiling = cfg.true_peak_ceiling - 0.15 - (0.15 * attempt)
            float_master = tmp / f'master_{attempt}.wav'
            master_premaster(premaster, float_master, cfg, pre_qc['input_i'], ceiling)
            convert_float_to_pcm(float_master, result_flac, cfg.ffmpeg, 24)
            final_qc = scan_loudness(result_flac, cfg.ffmpeg)
            attempts.append({"attempt": attempt+1, "limit_dBFS": ceiling, "true_peak_dBTP": final_qc['input_tp']})
            if final_qc['input_tp'] <= cfg.true_peak_ceiling + 0.05:
                break
        else:
            raise RuntimeError(f'Unable to satisfy true peak ceiling: {attempts}')
        if sample_count(result_flac) != source_info:
            raise RuntimeError('Output format/frame mismatch')
        if fingerprint != sha256(cfg.input):
            raise RuntimeError('Input changed during processing')
        result16 = cfg.output.with_name(cfg.output.stem + '_16bit.flac')
        if cfg.compatible_16bit:
            convert_float_to_pcm(float_master, tmp/'result16.flac', cfg.ffmpeg, 16)
            if sample_count(tmp/'result16.flac') != source_info:
                raise RuntimeError('16-bit frame count mismatch')
        # Publish after all QC, never partially overwrite a source file.
        os.replace(result_flac, cfg.output)
        if cfg.compatible_16bit:
            shutil.copyfile(tmp/'result16.flac', result16)
        if cfg.keep_premaster:
            shutil.copyfile(premaster, cfg.output.with_name(cfg.output.stem + '_PREMASTER_float32.wav'))
    report = {"backend": "spotify_pedalboard_plus_ffmpeg_astra", "input": str(cfg.input),
              "input_sha256": fingerprint, "output": str(cfg.output),
              "output_sha256": sha256(cfg.output), "input_frames": source_info[0],
              "sample_rate": source_info[1], "premaster": notes,
              "premaster_loudnorm": pre_qc, "final_loudnorm": final_qc,
              "ebur128_lufs": independently_scan_ebur128(cfg.output, cfg.ffmpeg),
              "attempts": attempts, "config": {**asdict(cfg), 'input': str(cfg.input), 'output': str(cfg.output)},
              "subjective_listening_test": "NOT_PERFORMED",
              "native_phaselimiter": "NOT_USED", "source_separation": "NOT_USED"}
    cfg.output.with_suffix('.qc.json').write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding='utf-8')
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input', type=Path)
    p.add_argument('output', type=Path)
    p.add_argument('--target-lufs', type=float, default=-13.7)
    p.add_argument('--ceiling-dbtp', type=float, default=-1.4)
    p.add_argument('--lowmid-db', type=float, default=-0.35)
    p.add_argument('--presence-db', type=float, default=0.2)
    p.add_argument('--air-db', type=float, default=0.3)
    p.add_argument('--vst3', action='append', default=[])
    p.add_argument('--compatible-16bit', action=argparse.BooleanOptionalAction, default=True)
    p.add_argument('--keep-premaster', action='store_true')
    p.add_argument('--dry-run', action='store_true')
    args = p.parse_args()
    cfg=Config(input=args.input, output=args.output, target_lufs=args.target_lufs,
               true_peak_ceiling=args.ceiling_dbtp, lowmid_db=args.lowmid_db,
               presence_db=args.presence_db, air_db=args.air_db,
               vst3_paths=tuple(args.vst3), compatible_16bit=args.compatible_16bit,
               keep_premaster=args.keep_premaster, dry_run=args.dry_run)
    print(json.dumps(run(cfg), ensure_ascii=False, indent=2, default=str))

if __name__ == '__main__':
    main()