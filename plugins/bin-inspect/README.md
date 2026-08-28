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

Verified live against a real 1.66 MB ELF binary (`/usr/bin/gtkwave`):
correct type detection, entropy 6.11 bits/byte, real gzip 2.518:1 vs. geo
codec 1.433:1 (gzip wins, correctly reported as the expected/typical
result), and a real `readelf -h` dump. Also verified against an empty
file to confirm the known geo-codec empty-input crash (documented
elsewhere in this project) is sidestepped, not silently ignored.

## Requirements

- Python 3 on PATH (standard library only)
- Optional, each skipped cleanly if absent: `file`, `xxd`, `readelf`
  (all standard on most Linux systems via `file`/`vim-common`/`binutils`)

## Install

```
/plugin marketplace add ras2045/p18-tools-marketplace
/plugin install bin-inspect@p18-marketplace
```

## Structure

```
bin-inspect-plugin/
├── .claude-plugin/plugin.json
├── skills/bin-inspect/SKILL.md
└── scripts/
    ├── bin_inspect.py       # entry point
    ├── geo_pair_codec.py    # bundled from p18-tools
    └── wheel270_engine.py   # geo_pair_codec's dependency
```
