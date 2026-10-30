# TREBLO / phaselimiter bridge v0.1

**Status: optional command-line adapter, not a deployed web service.** TREBLO main currently contains the Strudel sample library; no mastering HTTP/backend server exists there to attach to. This module provides the callable interface for a future service integration.

The official third-party native phase_limiter must be installed separately, along with FFmpeg/FFprobe with SoXR support. No third-party binaries are bundled. The upstream phaselimiter project has an MIT-licensed core; redistribution of binaries must also respect dependency licenses.

## Example (Windows PowerShell)

    python tools/mastering/phaselimiter_bridge.py `
      "C:\Audio\PREMASTER_float32.wav" `
      "C:\Audio\MASTER_PhaseLimiter_24bit.flac" `
      --phase-limiter "C:\Tools\phaselimiter\phase_limiter.exe" `
      --target-lufs -13.7 --ceiling-dbtp -1.4

Or on Linux/macOS:

    python3 tools/mastering/phaselimiter_bridge.py ./work/PREMASTER_float32.wav ./delivery/master.flac --phase-limiter phase_limiter --target-lufs -13.7 --ceiling-dbtp -1.4

Programmatic interface: import Settings and master from tools.mastering.phaselimiter_bridge, then call master(Settings(source=Path(...), output=Path(...))).

## Design

1. Accept stereo WAV/FLAC premaster, validate audio and preserve original SHA-256.
2. Explicitly resample to stereo float32 WAV **44.1 kHz**: the native phaselimiter always processes internally at that rate, even when the original is 48 kHz.
3. Disable native auto-mastering, pre-compression, frequency filters, enhancement and reverb. Select native phase limiting with true-peak ceiling, 4x true-peak analysis, loudness reference, float32 WAV.
4. SoXR resample to original sample rate; apply a single TPDF pass when quantizing to FLAC24.
5. Rescan **final FLAC** with FFmpeg loudnorm input_* fields. Retry with a lower native ceiling when true peak exceeds the requested ceiling by more than 0.05 dB, maximum three attempts.
6. Confirm source SHA-256 unchanged, stereo, sample rate and duration (25ms tolerance). Only then atomically replace requested output and write a QC JSON next to it.

This backend **does not** run Astra restoration/EQ, performs no neural separation, and does not silently fall back to FFmpeg on missing native executable. Feed it the float32 premaster, not a previously limited master.

Target LUFS is advisory: native loudness measurement can disagree with FFmpeg. The delivered QC JSON contains actual LUFS, TP, LRA and the attempt history. Conversion 48 -> 44.1 -> 48 kHz is not bit transparent. The backend has no authenticated web UI, upload service, background queue or deployment configuration.

## Tests

    python -m unittest discover -s tests -p 'test_phaselimiter_bridge.py' -v

Tests use a **mock** phaselimiter CLI to verify orchestration, not native audio quality. Before production use, verify a real phaselimiter binary, latency, GR, true peak, mono compatibility, A/B at equal loudness and actual listening.

Official phaselimiter: https://github.com/ai-mastering/phaselimiter

Astra Codex technical standard: see draft PR #2 in this repository.
