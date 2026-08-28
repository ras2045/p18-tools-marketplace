# Overnight Build Log — 2026-08-28 (complete)

Autonomous continuation session: building useful plugins on top of this
project's real, tested foundations (geo compression, offline cache, HDL
sim/synth/wave, local Ollama), plus new general-purpose tools discovered
by scanning for genuine gaps in the community marketplace. Every plugin
below was gap-checked against the full 2,282-plugin community marketplace
before building (fetched fresh at each check —
`https://raw.githubusercontent.com/anthropics/claude-plugins-community/main/.claude-plugin/marketplace.json`
— count stayed at 2,282 across the run) and verified live against real
data before packaging. No user confirmation stops during this run per
explicit instruction; every decision below is my own call, logged so it's
easy to review or revert.

## Final state: 5 plugins, 11 real commands, all pushed + installed

1. **ollama-tools** v0.1.0 — `ollama-ask`, `ollama-embed`, `ollama-compare`
   (local Ollama query/embed/compare-vs-Claude).
2. **hdl-tools** v0.2.0 — `hdl-sim` (Icarus), `hdl-synth` (Yosys, real gate
   count/critical path, `--timing` for a real-but-approximate ns/MHz
   estimate from real sky130 Liberty data), `hdl-wave` (real VCD dump,
   optional GTKWave launch).
3. **bin-inspect** v0.4.0 — `bin-inspect` (entropy/hex/SHA-256/ELF/
   compression), `disasm` (objdump symbols + disassembly), `bindiff`
   (real byte-level diff, run-grouped), `checksum` (crc32/adler32/md5/
   sha1/sha256/sha512).
4. **prime-utils** v0.1.0 — `is-prime`, `factor`, `sieve`, `gap-residues`
   (deterministic primality/factoring/sieving + the real, recomputed-fresh
   mod-18 prime-gap-residue finding).
5. **p18-tools** v0.1.0 (pre-existing) — `geo-compress`, `cache-lookup`.

Every command above was run against real data before being shipped, not
just written and assumed correct — see "Real bugs found and fixed" below
for what that caught.

## Real bugs found and fixed this run

- `hdl_synth.py --timing`: MHz conversion was off by 1000x
  (`1000.0/total_ps` instead of `1e6/total_ps`) — caught by sanity-checking
  the printed number, fixed and reverified (4.33 ns → correctly 231.0 MHz,
  not 0.2 MHz).
- `bin_inspect.py`: guarded the known geo-pair-codec empty-input crash
  (documented in `HANDOFF_2026-08-27_to_28.md`) with a `size == 0` check —
  verified against a real empty file.
- `prime_utils.py`: `is-prime 1` originally printed "composite", which is
  mathematically wrong (1 is neither prime nor composite) — fixed before
  shipping.

No bugs found in `hdl_wave.py`, `disasm.py`, `bindiff.py`, or
`checksum.py` during live testing — each produced correct output on first
verification (VCD byte count sane and GTKWave opened it; real symbol
sizes/disassembly matched a freshly compiled test binary; bindiff
correctly isolated a real single-byte change to its exact offset;
checksum output matched system `md5sum`/`sha1sum`/`sha256sum`/`sha512sum`
exactly).

## System note (unrelated to this work, flagged not fixed)

Installing `gtkwave` via apt surfaced pre-existing broken package state:
`linux-image-7.0.0-28-generic`, the VirtualBox DKMS module, and `grafana`
all failed their post-install/DKMS steps. gtkwave itself installed fine.
Not touched — flagging in case it needs attention separately.

## Why the run stopped here

Final gap scan (fresh marketplace fetch) found only two categories of
remaining zero-competitor niches, both deliberately not built:
- **Too thin to be a real plugin**: a standalone Gray-code converter is a
  one-line bit operation, not a tool with enough surface area to justify
  its own command — and this project's own gate-level testing already
  found Gray-coded addressing doesn't help the one case it was tried on
  here, so there's no unique angle to add beyond a trivial wrapper.
- **Too project-specific to package generally**: the real AVX2 peek/poke
  pipeline (`lemniscate_quant_prototype/native/peek_poke_avx2.c`) only
  operates on this project's own 5-bit Union-codebook quantization format
  — packaging it as a public plugin would require every user to first
  produce P18-specific input data, which isn't a generally useful tool.
- **Formal verification** (SymbiYosys/sby): still a real gap, but `sby`
  isn't packaged via apt on this system, and a thin wrapper wouldn't be
  genuinely useful without the user also writing real SVA/PSL assertions —
  scoped out both times this was considered this session.
- **SBOM generation**: zero exact-term hits, but 14 plugins already touch
  "supply chain" loosely enough that claiming a clean gap here would need
  deeper investigation than this run did — left open, not built.

Every idea that was both a genuine gap *and* buildable on real, verifiable
ground got built. Stopping rather than padding the suite with thin or
overly-narrow additions.

## For a future session

- Check `claude plugin list` for current install state before assuming
  what's live — this log is a point-in-time record.
- If revisiting SBOM or formal verification, actually check whether the
  14 "supply chain" plugins already cover it and whether `sby` has become
  apt-installable, rather than re-deriving from scratch.
- The method used throughout (gap-check against the live marketplace →
  verify every command against real data before packaging → sync into
  `plugins/<name>/` → update `.claude-plugin/marketplace.json` → commit +
  push → `claude plugin marketplace update p18-marketplace` → install/
  reinstall) is worth reusing as-is for any future addition.
