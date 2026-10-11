# TREBLO v1.2.1-rc.5 — Codex Engineering Handoff

**Purpose:** Review, reproduce, validate, and integrate three Windows hotfixes from the user's TREBLO MIDI → Strudel converter into the *actual* converter codebase, WITHOUT restarting or refactoring the frozen baseline.

**GitHub repository:** `Izhevsky/TREBLO`  
**Current GitHub status:** Its `main` primarily contains samples and documentation, **not** the full rc.5 Windows converter source. This handoff and patch are therefore intentionally staged as a reviewable artifact, **not** applied to unrelated sample-bank files. Find and verify the real converter's canonical source before integration.

## Source authority and provenance

- Patch base: `TREBLO_v1.2.1_DEV_CHECKPOINT_Windows.zip`, release `v1.2.1-rc.5`, original reported build `e164fd6a744d182a`.
- Final patched Windows archive: `TREBLO_v1.2.1-rc.5_WINDOWS_KEY_SIGNATURE_FIX.zip`.
- Final hotfix build: `65a722e08877de0b`.
- Patch path: `TREBLO_rc5_WINDOWS_HOTFIX_for_Codex.patch`; its paths are **relative to** `treblo_midi_to_strudel/`.
- The patch was checked with `git apply --check`, applied to a fresh extraction of the original rc.5 archive, and the resulting 17 changed/added files were verified byte-for-byte against the final hotfix archive.
- The patch carries provenance/manifests and historical reports, **not only application code**. Review all files, especially generated/checksum files, before committing to the canonical converter repository.
- Never assume prior hotfix verification establishes successful Windows operation on the user's actual RHODES source.

## What users saw, and why it matters

1. **BUILD MISMATCH** — the Windows backend produced build `bff417203670560c` while the original archive frontend produced `e164fd6a744d182a`. File path separators were included in the content digest using native `str(Path)`, so the same files hashed differently across Linux and Windows. Fix `app/build_info.py` to use `.as_posix()` before hashing; check frontend/backend/runtime identity and stale-browser rejection. After the build hotfix, screenshot showed both at `366366b190edaa21`.
2. **Unexpected token 'I', "Internal S"... is not valid JSON** — a user selected only **COMPACT SAFE**, but attached `RHODES.wav`. Backend still unnecessarily decoded/aligned audio and could crash with a plain HTTP 500 body. Fix `app/cli.py` so audio alignment runs ONLY for explicitly selected `aligned` or `aligned_musical` mode. Fix `app/server.py` to produce meaningful JSON error responses, and `ui/app.js` to handle non-JSON responses defensively. User's next screenshot confirmed frontend/backend match on build `2896b80a50d67aaa` and surfaced a new, specific error.
3. **KeySignatureError: Could not decode key with 14 sharps and mode 0** — malformed MIDI key-signature meta-event (FF 59) causes Mido to fail before the canonical MIDI parser sees notes. Add narrow `app/midi_input_recovery.py`, only triggered by Mido's `KeySignatureError`: inspect actual MIDI message boundaries and replace *invalid key-signature payload bytes only* in a disposable in-memory copy with neutral C-major bytes. Preserve input bytes for `exact_midi.mid` and source SHA-256. Exclude substituted invalid key metadata from the derived key list and emit explicit diagnostics with original value, mode, track and tick. Do not transpose notes or alter original timing, velocity, tempo or controllers.

## Codex execution instructions — do these in order

1. **Discover actual checkout:** identify authoritative full converter source, current branch, `VERSION.json`, frozen baseline manifests, archive/checkpoint SHA-256, installed Windows package and any divergent branches. Do not use the `Izhevsky/TREBLO` sample repository as a false stand-in for a missing converter checkout.
2. **Inspect the entire patch and reports** before editing. Read `WINDOWS_BUILD_FIX_NOTES.md`, `WINDOWS_CONVERT_FIX_NOTES.md`, `WINDOWS_KEY_SIGNATURE_FIX_NOTES.md`, `HOTFIX_TEST_REPORT.md`, and `KEY_SIGNATURE_HOTFIX_TEST_REPORT.md` (all contained in the patch).
3. **Establish exact ancestry:** verify the actual source matches the rc.5 patch base. If not, generate a three-way comparison and selectively port the fixes with tests. NEVER force-apply patches, replace newer code with older code, or overwrite `main` blindly.
4. **Freeze audit:** diff `app/midi_reader.py`, MIDI parser, canonical timing, tempo map, exact emitter, compact safe, musical compact, alignment DSP and other declared frozen modules. Flag any inherited mismatch. Do not silently “repair” `app/exporter.py`: a divergence relative to the archived rc.3 freeze manifest was pre-existing in source rc.5 and is not caused by the hotfix.
5. **Build identity audit:** on Linux and Windows calculate the same stable build digest. Check whether a build stamp automatically updates `ui/app.js`, `VERSION.json`, manifest hashes and response headers. Test browser caching, stale `X-TREBLO-Build`, and accidental launch of the wrong local instance on port 8765.
6. **Mode isolation audit:** `COMPACT SAFE`, `EXACT`, `COMPACT MUSICAL`, and `QUANTIZED` must not decode/align WAV even when attached. `AUDIO ALIGNED MUSICAL` must require audio. `AUDIO ALIGNED EXACT` must retain its documented behavior and never be confused with Musical.
7. **Error handling audit:** validate HTTP statuses, JSON error schema, cleanup of temporary jobs/files, UI error text, logs, and traceback behavior. Do not expose sensitive paths, credentials or arbitrary exception text if the app ever becomes remotely accessible; localhost scope matters.
8. **MIDI key metadata audit:** test legal signatures `-7...+7`, major/minor; out-of-range signed fifths, invalid modes, extra track chunks, running status, SysEx, different VLQ sizes and malformed/truncated streams. Preserve raw input and all performance events. Unrecoverable structural corruption must fail closed; warn about sanitized metadata, and never silently change notes.
9. **Deterministic regression:** run all existing focused and full tests; add cases for attached WAV + Compact Safe, invalid FF59 +14, valid key-signature unchanged, corrupted MIDI rejected, source SHA preservation, accurate notes/durations/velocity/tempo/CC, and API error reporting.
10. **Real acceptance audio/MIDI:** request the user's actual `RHODES (Without Lead Vocal).mid` and `RHODES.wav` if absent. Validate original MIDI with Compact Safe, compare canonical events with exported Strudel runtime events, verify audition, and then separately test selected aligned mode. Test the primary real benchmark **Paul Pooze — VOLOGDA** with original MIDI plus reference WAV.
11. **Runtime/browser/Windows gates:** test real Strudel load/query/play/stop/restart, sample readiness and audible output, small/medium/large files, browser responsiveness, and a fresh Windows install. Test that no mismatched server is already bound to 127.0.0.1:8765.
12. **Release discipline:** treat as `DEV CHECKPOINT` until all gates pass. Report `PASS / FAIL / NOT RUN / BLOCKED`, evidence paths, actual current hashes, runtime profile, warnings, defects found, tests, and exact build. Create a dedicated PR in the actual converter source repository/branch when identified. Do not auto-merge anything.

## Acceptance criteria

- No `BUILD MISMATCH` on a clean Windows install; the frontend/backend source digest agrees and an old browser build is detected.
- No WAV DSP for MIDI-only selected modes, even with an audio file attached.
- Unexpected failures appear as intelligible diagnostics rather than JSON parsing exceptions.
- Invalid FF59 key metadata can be quarantined without modifying any MIDI performance data; original source is retained bit-identically.
- Exact and Compact emit original MIDI timing with no hidden quantization.
- Actual Strudel output verified by event query and playback; no critical browser freeze.
- Actual RHODES and VOLOGDA tests are completed and documented.
- Frozen source changes are limited to demonstrated defects; regression suite passes.
- End user receives reproducible Windows instructions and updated provenance.

## Verification already performed vs. still required

| Gate | Evidence |
|---|---|
| Local application patch applies cleanly to original rc.5 archive | **PASS**, `git apply --check` and application |
| Resulting 17 files byte-identical to final hotfix | **PASS**, local comparison |
| Focused hotfix tests | **77 PASS**, per prior hotfix test report |
| Entire pytest suite | **NOT COMPLETED**, previously timed out |
| User's actual RHODES MIDI/WAV | **NOT RUN**; files not available in our sandbox |
| Native Windows acceptance + audible/browser acceptance | **NOT RUN** |
| Legacy frozen `app/exporter.py` manifest discrepancy | **OPEN / INHERITED** |

## Minimal patch workflow

From the **verified original converter rc.5 code root**, not from the sample-bank GitHub root:

```bash
git apply --check /path/to/TREBLO_rc5_WINDOWS_HOTFIX_for_Codex.patch
git apply /path/to/TREBLO_rc5_WINDOWS_HOTFIX_for_Codex.patch
python -m pytest -q tests/test_bad_key_signature_hotfix.py tests/test_build_provenance.py tests/test_server.py
```

If any patch hunk fails, **stop** and inspect ancestry. Do not force apply. The exact command and Python environment are implementation-dependent; run full tests and version stamping before shipping. Test reports in the patch are historical evidence, **not** new executions by Codex.

## Requested Codex deliverables

1. Source audit and exact base/commit identification.
2. Reviewed/adapted source changes with tests; no unverified cross-version replacement.
3. Complete regression report, provenance and known blockers.
4. Real browser/Strudel and Windows user acceptance evidence.
5. Proper converter-source PR, with clear diff and rollback steps.
6. No final-release claim until the actual required gates pass.

**Please begin by verifying the actual converter checkout and patch ancestry. Do not start a rewrite or make unrelated audio/producer feature changes.**
