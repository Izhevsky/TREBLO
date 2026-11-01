# TREBLO Astra Audio v2 — Pedalboard / MSST bridge

**Status:** real Pedalboard + FFmpeg mastering backend with CPU tests. MSST is an **optional adapter only**; no checkpoint bundled or claimed. This is not an HTTP service or a deployed website.

## Quick start

Python 3.10+ and FFmpeg with SoXR on PATH:

```sh
pip install pedalboard numpy soundfile
python tools/mastering/astra_pedalboard.py input.wav output.flac --keep-premaster --target-lufs -13.7 --ceiling-dbtp -1.4
```

Default EQ is **deliberately tiny**: 360 Hz −0.35 dB, 3 kHz +0.2 dB, 9 kHz +0.3 dB. These are *provisional choices*, not universal standards; zero them with `--lowmid-db 0 --presence-db 0 --air-db 0` for a transparent path. Add a real Windows VST3 effect using `--vst3 C:\\VST3\\plugin.vst3`, provided it is installed, licensed, compatible and frame-preserving. Plugins are third-party code and require local review.

Inputs are never modified; SHA-256 checked before/after. Chunked Pedalboard processing keeps state, rejects NaNs and altered frame counts. It outputs float32 WAV with sample peak −6 dBFS, then a separate 4× SoXR / FFmpeg limiter branch with a retrying true-peak ceiling. Both FLAC24 and FLAC16 are independently quantized from the same **post-limiter float signal**, each with one TPDF pass. The final FLAC is independently checked using loudnorm input_* and ebur128. JSON QC includes whether listening occurred (not performed automatically).

**Limitations**: The script cannot claim musical improvement from metrics; it does not remove AI artifacts automatically or separate sources. An arbitrary VST may cause latency, fail to reset state, introduce a long reverb tail, or change sample count; long-tail plugins need a specialized offline bounce before production. Do not feed an already-limited master for another limiting pass. When using the CPU prototype, compare at equal loudness with the existing favorite.

## MSST: experimental external stage

MSST is independently maintained and requires compatible YAML + checkpoint and correct PyTorch/CUDA installation. Example:

```sh
pip install 'msst[bs_roformer]'
python tools/mastering/msst_bridge.py separate --config models/model.yaml --checkpoint models/model.ckpt --input-folder input --output-folder stems --dry-run
# after inspecting command and installed model, remove --dry-run
python tools/mastering/msst_bridge.py qc --mix input/track.wav --stems stems/track_bass.wav stems/track_other.wav
```

The QC sums complementary stems and calculates residual energy in dB relative to the original; this is **not an SDR metric against ground truth**. It never automatically accepts a stem remix. Some models output only a target stem; do not apply this test to non-complementary outputs. Any input/reference resampling or model bleed must be addressed before a rework.

## Recommended integration

Astra Restoration → optional MSST stem experiment + listening QC → Pedalboard source/steam mix (separate routing not yet provided) → float32 premaster → choose **either** Astra FFmpeg or optional native phaselimiter backend (separate script) → FLAC24/16 → final-file QC + equal-loudness listening comparison.

**Currently:** Pedalboard DSP and Astra/FFmpeg branch can be executed; native phaselimiter is a separate optional bridge. Full production service, headless VST compatibility matrix, GPU MSST, and user authentication are not implemented. Never claim these are already deployed.

License notice: Spotify Pedalboard is GPL-3.0 (check package and repository's current licensing and third-party VST obligations before distributing a combined service). MSST and model checkpoints have separate terms. No third-party plugin binaries or weights are included here.