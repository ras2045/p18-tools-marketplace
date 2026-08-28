# Overnight Build Log — started 2026-08-28

Autonomous continuation session: building useful plugins on top of this
project's real, tested foundations (geo compression, offline cache, HDL
sim/synth/wave, local Ollama). Every plugin below was gap-checked against
the full 2,282-plugin community marketplace before building (zero
competing plugins for each niche at build time) and verified live against
real data before packaging — same standard as the rest of this session.
No user confirmation stops during this run per explicit instruction; all
decisions below are my own calls, listed so they're easy to review/revert.

## Plugins shipped this run (all pushed + installed)

1. **ollama-tools** (earlier, pre-overnight) — ask/embed/compare against
   local Ollama.
2. **hdl-tools** (earlier, pre-overnight; extended overnight) —
   hdl-sim, hdl-synth (+ `--timing` real-ns estimate, added overnight),
   hdl-wave (added overnight, real VCD + GTKWave).
3. **bin-inspect** (overnight) — entropy/hex/SHA-256/ELF-header/
   compression-comparison file inspector.
4. **prime-utils** (overnight) — deterministic primality, factoring,
   sieving, and the real mod-18 gap-residue finding, recomputed fresh
   each run (not hardcoded).

## Real bugs found and fixed this run

- `hdl_synth.py --timing`: MHz conversion was off by 1000x
  (`1000.0/total_ps` instead of `1e6/total_ps`) — caught by sanity-checking
  the printed number against the known ns figure, fixed and reverified.
- `bin_inspect.py`: guarded the known geo-pair-codec empty-input crash
  (documented in `HANDOFF_2026-08-27_to_28.md`) with a `size == 0` check
  rather than letting it propagate — verified against a real empty file.
- `prime_utils.py`: `is-prime 1` originally printed "composite", which is
  mathematically wrong (1 is neither prime nor composite) — fixed before
  shipping.

## System note (unrelated to this work, flagged not fixed)

Installing `gtkwave` via apt surfaced pre-existing broken package state:
`linux-image-7.0.0-28-generic`, the VirtualBox DKMS module, and `grafana`
all failed their post-install/DKMS steps. gtkwave itself installed fine.
Not touched — flagging in case it needs attention separately.

## Still open / candidates not yet built

Checked and genuinely available (zero marketplace competitors) but not
yet built, in case a future session wants to pick one up:
- Disassembly/reverse-engineering wrapper (objdump/readelf are already
  used lightly in bin-inspect; a dedicated `objdump -d` + symbol-table
  browser could go further) — bigger scope, no real code to reuse yet.
- SBOM generation — zero exact-term hits, but 14 plugins already touch
  "supply chain" loosely; would need to check those aren't already doing
  this under different branding before claiming a gap.
- Formal verification (SymbiYosys/sby) — real gap, but `sby` isn't
  packaged via apt on this system and a thin wrapper wouldn't be
  genuinely useful without the user also writing real SVA assertions;
  scoped out for now (see earlier session decision).

This file will be updated as the overnight run continues.
