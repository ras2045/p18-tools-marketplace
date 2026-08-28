# Binary File Inspector — Claude Code Plugin

Real file inspection: size, SHA-256, Shannon entropy, hex preview, ELF
header, and an honest gzip-vs-geo-codec compression comparison. No
competing "entropy"/"hex dump"/"binary inspect" plugin existed in the
community marketplace at the time this was built (checked against all
2,282 listed plugins).

## What's real here

- **`/bin-inspect:bin-inspect`** — reads the actual file bytes and reports:
  real size and SHA-256, real Shannon entropy (standard formula, not
  estimated), a real `xxd` hex preview of the first 128 bytes, a real
  `readelf -h` header if the file is ELF, and a real compression
  comparison between gzip -9 and this project's geo-pair codec — reported
  honestly either way, including the (common) case where gzip wins.

- **`/bin-inspect:disasm`** — lists a binary's real defined function
  symbols (via `objdump -t`, sorted by size), or disassembles one named
  function (`objdump -d --disassemble=NAME -M intel`).

- **`/bin-inspect:bindiff`** — real byte-level diff between two files,
  differing offsets grouped into contiguous runs with real hex context
  from both files. No competing "bindiff"/"hexdiff"/"binary diff" plugin
  existed in the community marketplace at build time.

Verified live against a real 1.66 MB ELF binary (`/usr/bin/gtkwave`):
correct type detection, entropy 6.11 bits/byte, real gzip 2.518:1 vs. geo
codec 1.433:1 (gzip wins, correctly reported as the expected/typical
result), and a real `readelf -h` dump. Also verified against an empty
file to confirm the known geo-codec empty-input crash (documented
elsewhere in this project) is sidestepped, not silently ignored.
`disasm` was verified against a freshly compiled, symbol-preserving test
binary: correctly extracted 10 real function symbols with real sizes, and
correctly disassembled a 2-argument `add()` function to matching real
x86-64 instructions. `bindiff` was verified against identical files
(correctly reports identical), a real single-byte modification at a known
offset (correctly isolates exactly offset 0x3e8), and files of different
sizes (correctly reports the size delta and diffs only the common
region).

## Requirements

- Python 3 on PATH (standard library only)
- Optional, each skipped cleanly if absent: `file`, `xxd`, `readelf`
  (all standard on most Linux systems via `file`/`vim-common`/`binutils`)
- `objdump` for `disasm` (part of `binutils`, usually preinstalled)

## Install

```
/plugin marketplace add ras2045/p18-tools-marketplace
/plugin install bin-inspect@p18-marketplace
```

## Structure

```
bin-inspect-plugin/
├── .claude-plugin/plugin.json
├── skills/
│   ├── bin-inspect/SKILL.md
│   ├── disasm/SKILL.md
│   └── bindiff/SKILL.md
└── scripts/
    ├── bin_inspect.py       # entry point for bin-inspect
    ├── disasm.py            # entry point for disasm
    ├── bindiff.py           # entry point for bindiff
    ├── geo_pair_codec.py    # bundled from p18-tools
    └── wheel270_engine.py   # geo_pair_codec's dependency
```
