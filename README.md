# TREBLO Lo-Fi House Sample Library

Custom sample library for Strudel projects focused on Lo-Fi House, Stoner House, Dusty House, Analog House and related late-1980s / early-1990s aesthetics.

## Strudel usage

```javascript
samples('github:Izhevsky/TREBLO')
```

The repository uses `strudel.json` in the root as the sample map. Try `examples/cc0_bank_audition.js` after loading the repository.

## Sound design note

The public-domain banks are kept deliberately dry. Finished character should come from selection plus subtle Strudel processing: filtering, envelope shaping, gain staging, short room, small timing offsets and restrained saturation.

## Conventions

- WAV PCM preferred
- 44.1 kHz or 48 kHz
- 16-bit or 24-bit
- ASCII filenames, lowercase, underscores
- no spaces in filenames
- short machine-readable bank names prefixed with `lh_`
- keep source/provenance information in `SOURCES.md`
- keep Treblo generation prompts in `TREBLO_PROMPTS.md`
- keep requested future samples in `SAMPLE_REQUESTS.md`

See `CATALOG.md` for the library inventory and `LICENSES.md` for licensing notes.


## Reusable production playbook

Approved Strudel hooks, groove DNA, sound-layering recipes, runtime lessons and arrangement blueprints are maintained in:

- `docs/TREBLO_STRUDEL_PLAYBOOK.md`
- `examples/screenshot_groove_reusable_core_v1.js`

The playbook separates repository-owned/redistributable TREBLO assets from references to Strudel built-in banks.
